from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from .forms import TimeEntryForm, InvoiceForm
from .models import TimeEntry, Matter, WIP, Invoice, InvoiceLine, Ledger
from django.db import transaction

# -- Views --

# Index
def index(request):
    return render(request, "better_bill_project/index.html")

# Time Entry Form
def record_time(request):
    recent_entries = TimeEntry.objects.select_related(
        "matter", "fee_earner"
    ).order_by("-created_at")[:10]

    if request.method == "POST":
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            te = form.save()  # <-- only save TimeEntry
            messages.success(request, "Time entry saved.")
            return redirect("record-time")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TimeEntryForm()

    return render(request, "better_bill_project/record.html", {
        "form": form,
        "recent_entries": recent_entries,
    })

# --- AJAX: returns option list for matters by client (value = matter_number)
def ajax_matter_options(request):
    client_id = request.GET.get("client")
    matters = Matter.objects.filter(client_id=client_id, closed_at__isnull=True).order_by("matter_number") if client_id else []
    html = render_to_string("partials/matter_options.html", {"matters": matters})
    return HttpResponse(html)


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

                    messages.success(request, "Invoice created successfully.", extra_tags="invoice")
        return redirect("create-invoice")  # or wherever you want to land post-PRG
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
