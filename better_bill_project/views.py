from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from .forms import TimeEntryForm, InvoiceForm
from .models import TimeEntry, Matter, WIP, Invoice, InvoiceLine, Ledger
from django.db import transaction

# -- Views --

# Index
def index(request):
    return render(request, "better_bill_project/index.html")

# Time Entry Form
def record_time(request):
    if request.method == "POST":
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                entry = form.save()  # saves TimeEntry

                # ensure there is exactly one WIP for this TimeEntry (OneToOne)
                WIP.objects.update_or_create(
                    time_entry=entry,                 # OneToOne anchor (cannot be NULL)
                    defaults={
                        "client":        entry.client,
                        "matter":        entry.matter,
                        "fee_earner":    entry.fee_earner,
                        "activity_code": entry.activity_code,
                        "hours_worked":  entry.hours_worked,
                        "narrative":     entry.narrative,
                        "status":        "unbilled",
                    },
                )

            messages.success(request, f"Time entry saved for {entry.matter.matter_number}.")
            return redirect("record-time")
    else:
        form = TimeEntryForm()

    recent_entries = (
        TimeEntry.objects
        .select_related("matter", "matter__client", "fee_earner")
        .order_by("-created_at")[:10]
    )
    return render(request, "better_bill_project/record.html", {"form": form, "recent_entries": recent_entries})


# --- AJAX: returns option list for matters by client (value = matter_number)
def matter_options(request):
    client_id = request.GET.get("client")
    if not client_id:
        return HttpResponse('<option value="">— Select matter —</option>')
    qs = Matter.objects.filter(client_id=client_id, closed_at__isnull=True).order_by("matter_number")
    # VALUE = m.id (numeric)
    options = ['<option value="">— Select matter —</option>'] + [
        f'<option value="{m.id}">{m.matter_number} — {m.description}</option>' for m in qs
    ]
    return HttpResponse("".join(options))


def _next_invoice_number():
    """
    Generate the next 6-digit sequential invoice number as a string.
    Starts at '000001'. Uses latest existing Invoice.number if numeric.
    """
    last = Invoice.objects.order_by("-id").first()
    n = 0
    if last:
        # try to parse numeric Invoice.number safely
        try:
            n = int("".join(ch for ch in last.number if ch.isdigit()))
        except (TypeError, ValueError):
            n = last.id or 0  # fallback
    return f"{n + 1:06d}"

def create_invoice(request):
    readonly_number = _next_invoice_number()
    readonly_date = timezone.localdate()
    readonly_tax = Decimal("20.00")  # percent

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            wip_ids = request.POST.getlist("wip_ids")
            if not wip_ids:
                messages.error(request, "Select at least one WIP item to invoice.")
            else:
                with transaction.atomic():
                    inv = form.save(commit=False)
                    inv.number = readonly_number
                    inv.invoice_date = readonly_date
                    inv.tax_rate = readonly_tax
                    inv.save()

                    items = list(
                        WIP.objects
                        .select_related("fee_earner__role", "matter", "matter__client")
                        .filter(id__in=wip_ids, status="unbilled")
                    )
                    if not items:
                        messages.error(request, "Selected WIP items are no longer available.")
                        return redirect("create-invoice")

                    lines = []
                    for w in items:
                        rate = getattr(getattr(w.fee_earner, "role", None), "rate", Decimal("0.00"))
                        amount = (Decimal(w.hours_worked) * rate).quantize(Decimal("0.01"))
                        desc = w.narrative or f"{w.matter.matter_number} — {w.activity_code or 'Work'}"
                        lines.append(InvoiceLine(
                            invoice=inv, wip=w, desc=desc,
                            hours=w.hours_worked, rate=rate, amount=amount
                        ))
                    InvoiceLine.objects.bulk_create(lines)
                    WIP.objects.filter(id__in=[w.id for w in items]).update(status="billed")

                    Ledger.objects.create(
                        invoice=inv, client=inv.client, matter=inv.matter,
                        subtotal=inv.subtotal, tax=inv.tax_amount, total=inv.total,
                        status="draft",
                    )

                    messages.success(request, f"Invoice {inv.number} created. Total: £{inv.total}")
                    return redirect("create-invoice")
    else:
        form = InvoiceForm(request.GET or None)

    # --- Build WIP list for current selection (works for GET and invalid POST) ---
    # Start from a base queryset so we don't lose results when only 'matter' is set.
    cid = form.data.get("client") or None
    mid = form.data.get("matter") or None

    wip_qs = (WIP.objects
            .select_related("matter", "matter__client", "fee_earner", "activity_code")
            .filter(status="unbilled"))

    if cid:
        wip_qs = wip_qs.filter(matter__client_id=cid)
    if mid:
        try:
            wip_qs = wip_qs.filter(matter_id=int(mid))
        except (TypeError, ValueError):
            pass


    wip_items = wip_qs.order_by("matter__matter_number", "created_at")


    return render(
        request,
        "better_bill_project/create_invoice.html",
        {
            "form": form,
            "wip_items": wip_items,
            "readonly_number": readonly_number,
            "readonly_date": readonly_date,
            "readonly_tax": readonly_tax,
        },
    )



# View Invoice
def view_invoice(request):
    return render(request, "better_bill_project/view_invoice.html")
