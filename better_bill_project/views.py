from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from .forms import TimeEntryForm, InvoiceForm
from .models import TimeEntry, Matter, WIP, Invoice, InvoiceLine, Ledger
from django.db import transaction

# Create your views here.

def index(request):
    return render(request, "better_bill_project/index.html")

def record_time(request):
    if request.method == "POST":
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f"Time entry saved for {entry.matter.matter_number}.")
            return redirect("record-time")
    else:
        form = TimeEntryForm()

    recent_entries = TimeEntry.objects.select_related("client", "matter", "fee_earner").order_by("-created_at")[:10]
    return render(request, "better_bill_project/record.html", {"form": form, "recent_entries": recent_entries})

# --- AJAX: return <option> list for matters by client ---

def matter_options(request):
    client_id = request.GET.get("client")
    if not client_id:
        return HttpResponse('<option value="">— Select matter —</option>')
    qs = Matter.objects.filter(client_id=client_id, closed_at__isnull=True).order_by("matter_number")
    options = ['<option value="">— Select matter —</option>'] + [
        f'<option value="{m.id}">{m.matter_number} — {m.description}</option>' for m in qs
    ]
    return HttpResponse("".join(options))

def view_invoice(request):
    return render(request, "better_bill_project/view_invoice.html")

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InvoiceForm
from .models import WIP, Invoice, InvoiceLine, Ledger

def _next_invoice_number():
    last = Invoice.objects.order_by("-id").first()
    n = 0
    if last:
        try:
            n = int("".join(ch for ch in last.number if ch.isdigit()))
        except (TypeError, ValueError):
            n = last.id or 0
    return f"{n + 1:06d}"

def create_invoice(request):
    readonly_number = _next_invoice_number()
    readonly_date = timezone.localdate()
    readonly_tax = Decimal("20.00")

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
                        WIP.objects.select_related("fee_earner__role", "matter")
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

    # 🔽 THIS BLOCK MUST BE INSIDE THE FUNCTION (not top-level)
    wip_qs = WIP.objects.none()
    cid = form.data.get("client") if hasattr(form, "data") else None
    mid = form.data.get("matter") if hasattr(form, "data") else None
    if cid:
        wip_qs = (
            WIP.objects
            .select_related("matter", "fee_earner", "activity_code", "matter__client")
            .filter(matter__client_id=cid, status="unbilled")
        )
        if mid:
            wip_qs = wip_qs.filter(matter_id=mid)
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
