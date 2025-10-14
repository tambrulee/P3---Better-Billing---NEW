from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from .forms import TimeEntryForm
from .models import TimeEntry, Matter, WIP, Invoice, InvoiceLine, Ledger
from django.db import transaction
from .forms import InvoiceForm

# Create your views here.

def index(request):
    return render(request, "better_bill_project/index.html")

def create_invoice(request):
    return render(request, "better_bill_project/create_invoice.html")

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


def create_invoice(request):
    """
    GET  -> shows form; when client/matter chosen, lists unbilled WIP items.
    POST -> creates Invoice + InvoiceLines, marks WIP billed, writes Ledger.
    """
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            wip_ids = request.POST.getlist("wip_ids")  # checkbox values
            if not wip_ids:
                messages.error(request, "Select at least one WIP item to invoice.")
                return render(request, "better_bill_project/create_invoice.html", {"form": form, "wip_items": []})

            with transaction.atomic():
                invoice = form.save()  # draft ledger will be created below
                # fetch WIP items
                items = list(
                    WIP.objects.select_related("fee_earner__role", "matter")
                    .filter(id__in=wip_ids, status="unbilled")
                )

                if not items:
                    messages.error(request, "Selected WIP items are no longer available (already billed?).")
                    return redirect("create-invoice")

                # build lines
                lines = []
                for w in items:
                    # get rate from fee earner role (fallback to 0)
                    rate = getattr(getattr(w.fee_earner, "role", None), "rate", Decimal("0.00"))
                    amount = (Decimal(w.hours_worked) * rate).quantize(Decimal("0.01"))
                    desc = w.narrative or f"{w.matter.matter_number} — {w.activity_code or 'Work'}"
                    lines.append(InvoiceLine(
                        invoice=invoice,
                        wip=w,
                        desc=desc,
                        hours=w.hours_worked,
                        rate=rate,
                        amount=amount,
                    ))
                InvoiceLine.objects.bulk_create(lines)

                # mark WIP billed
                WIP.objects.filter(id__in=[w.id for w in items]).update(status="billed")

                # create ledger snapshot
                ledger = Ledger.objects.create(
                    invoice=invoice,
                    client=invoice.client,
                    matter=invoice.matter,
                    subtotal=invoice.subtotal,
                    tax=invoice.tax_amount,
                    total=invoice.total,
                    status="draft",
                )

                messages.success(request, f"Invoice {invoice.number} created. Total: {invoice.total}")
                return redirect("create-invoice")
    else:
        form = InvoiceForm(request.GET or None)

    # For GET: if a client/matter is chosen, show unbilled WIP to pick
    wip_qs = WIP.objects.none()
    cid = form.data.get("client") if hasattr(form, "data") else None
    mid = form.data.get("matter") if hasattr(form, "data") else None
    if cid:
        wip_qs = WIP.objects.select_related("matter", "fee_earner", "activity_code") \
            .filter(client_id=cid, status="unbilled")
        if mid:
            wip_qs = wip_qs.filter(matter_id=mid)

    return render(
        request,
        "better_bill_project/create_invoice.html",
        {"form": form, "wip_items": wip_qs.order_by("matter__matter_number", "created_at")}
    )
