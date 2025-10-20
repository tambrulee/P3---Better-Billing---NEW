from decimal import Decimal
from django.utils import timezone
from django.core.paginator import Paginator
import pdfkit
from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from .forms import TimeEntryForm, InvoiceForm, TimeEntryQuickEditForm
from .models import TimeEntry, Client, Matter
from .models import WIP, Invoice, InvoiceLine, Ledger, Personnel, ActivityCode
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from playwright.sync_api import sync_playwright


# -- Views --

def index(request):
    # Unbilled WIP
    wip_qs = (
        WIP.objects
        .select_related("matter", "client")
        .filter(status="unbilled")
        .order_by("-created_at")
    )
    wip_total_hours = wip_qs.aggregate(
        total=Sum("hours_worked"))["total"] or Decimal("0.0")

    # Draft/Posted via Ledger status (only invoices that HAVE a ledger)
    draft_qs = (
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .filter(ledger__status="draft")
        .order_by("-created_at")[:10]
    )
    posted_qs = (
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .filter(ledger__status="posted")
        .order_by("-created_at")[:10]
    )

    # Totals (aggregate over related ledger fields)
    draft_totals = draft_qs.aggregate(
        subtotal=Sum("ledger__subtotal"),
        tax=Sum("ledger__tax"),
        total=Sum("ledger__total"),
    )
    post_totals = posted_qs.aggregate(
        subtotal=Sum("ledger__subtotal"),
        tax=Sum("ledger__tax"),
        total=Sum("ledger__total"),
    )

    context = {
        "wip_items": wip_qs[:10],
        "wip_total_hours": wip_total_hours,

        "draft_invoices": draft_qs,
        "draft_subtotal": draft_totals["subtotal"] or Decimal("0.00"),
        "draft_tax":      draft_totals["tax"]      or Decimal("0.00"),
        "draft_total":    draft_totals["total"]    or Decimal("0.00"),

        "posted_invoices": posted_qs,
        "post_subtotal": post_totals["subtotal"] or Decimal("0.00"),
        "post_tax":      post_totals["tax"]      or Decimal("0.00"),
        "post_total":    post_totals["total"]    or Decimal("0.00"),
    }
    return render(request, "better_bill_project/index.html", context)

# Time Entry Form
@login_required
def record_time(request):
    # Who can see everything? (Partners/Admins – reusing your post_invoice perm)
    is_partner = request.user.has_perm(
        "better_bill_project.post_invoice") or request.user.is_superuser
    fe_filter = request.GET.get("fe")
    personnel_for_user = getattr(
        request.user, "personnel_profile", None)

    base_qs = (TimeEntry.objects
               .select_related("matter", "fee_earner", "wip")
               .order_by("-created_at"))

    if is_partner:
        if fe_filter:
            base_qs = base_qs.filter(fee_earner_id=fe_filter)
        fee_earners = Personnel.objects.order_by("initials")
    else:
        if personnel_for_user:
            base_qs = base_qs.filter(fee_earner=personnel_for_user)
        else:
            base_qs = base_qs.none()
        fee_earners = None

    recent_entries = base_qs[:20]
    activity_codes = ActivityCode.objects.all().order_by("activity_code")

    # --- Handle "quick edit" update submissions ---
    if request.method == "POST" and request.POST.get("update_id"):
        te = get_object_or_404(
            TimeEntry.objects.select_related("wip"),
            pk=request.POST["update_id"])

        # Permission: non-partners can only edit their own entries
        if not is_partner:
            if not personnel_for_user or te.fee_earner_id != personnel_for_user.id:
                messages.error(
                    request, "You cannot edit this entry.")
                return redirect("record-time")

        # Only allow edits when still unbilled
        if not hasattr(te, "wip") or te.wip.status != "unbilled":
            messages.error(
                request, "This entry is billed and can’t be edited.")
            return redirect("record-time")

        form_qe = TimeEntryQuickEditForm(request.POST, instance=te)
        if form_qe.is_valid():
            with transaction.atomic():
                form_qe.save()  # signal will sync WIP fields
            messages.success(request, "Time entry updated.")
            # preserve partner filter if present
            return redirect(
                f"record-time{'?fe='+fe_filter if is_partner and fe_filter else ''}")
        else:
            # Fall through to re-render page with the row open and errors shown
            pass

    # --- Normal create form flow (unchanged) ---
    if request.method == "POST" and not request.POST.get("update_id"):
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Time entry saved.")
            return redirect("record-time")
        else:
            messages.error(request, "Please correct the errors below.")
        form_qe = None  # not used in this branch
    else:
        form = TimeEntryForm()
        form_qe = None

        return render(request, "better_bill_project/record.html", {
        "form": form,
        "recent_entries": recent_entries,
        "is_partner": is_partner,
        "fee_earners": fee_earners,
        "selected_fe": fe_filter,
        "activity_codes": activity_codes,
        "me_personnel_id": getattr(personnel_for_user, "id", None),
    })

# Delete Time Entry

@login_required
@require_POST
def delete_time_entry(request, pk):
    # Reuse your existing permission rule
    is_partner = request.user.has_perm(
        "better_bill_project.post_invoice") or request.user.is_superuser
    personnel_for_user = getattr(request.user, "personnel_profile", None)

    # Keep it strict + cheap
    te = get_object_or_404(
        TimeEntry.objects.select_related("wip", "fee_earner"),
        pk=pk
    )

    # Only allow deletes when still UNBILLED
    if not hasattr(te, "wip") or te.wip.status != "unbilled":
        messages.error(
            request, "This entry has been billed and can’t be deleted.")
        return _back_to_record_time(request)

    # Ownership rule: non-partners can only delete their own
    if not is_partner:
        if not personnel_for_user or te.fee_earner_id != personnel_for_user.id:
            messages.error(
                request, "You can only delete your own unbilled entries.")
            return _back_to_record_time(request)

    te.delete()
    messages.success(request, "Time entry deleted.")
    return _back_to_record_time(request)


def _back_to_record_time(request):
    """
    Preserve the current fee earner filter (?fe=) if it was present.
    Prefer hidden field sent by the form; otherwise fall back to Referer.
    """
    fe = request.POST.get("fe")
    if fe:
        return redirect(f"{reverse('record-time')}?fe={fe}")
    # Fallback: simple redirect (or use HTTP_REFERER if you prefer)
    return redirect("record-time")

# --- AJAX: returns option list for matters by client (value = matter_number)
def ajax_matter_options(request):
    client_id = request.GET.get("client")
    matters = Matter.objects.filter(
        client_id=client_id, closed_at__isnull=True).order_by(
            "matter_number") if client_id else []
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
                        messages.error(request,
                                       "Selected WIP items are no longer available.")
                        return redirect("create-invoice")

                    lines = []
                    for w in items:
                        rate = getattr(
                            getattr(
                                w.fee_earner, "role", None), "rate", Decimal("0.00"))
                        amount = (
                            Decimal(
                                w.hours_worked) * rate).quantize(Decimal("0.01"))
                        desc = w.narrative or f"{
                            w.matter.matter_number} — {w.activity_code or 'Work'}"
                        lines.append(InvoiceLine(
                            invoice=inv, wip=w, desc=desc,
                            hours=w.hours_worked, rate=rate, amount=amount
                        ))
                    InvoiceLine.objects.bulk_create(lines)
                    WIP.objects.filter(
                        id__in=[w.id for w in items]).update(status="billed")

                    Ledger.objects.create(
                        invoice=inv, client=inv.client, matter=inv.matter,
                        subtotal=inv.subtotal, tax=inv.tax_amount, total=inv.total,
                        status="draft",
                    )

                    messages.success(
                        request, "Invoice created successfully.", extra_tags="invoice")
        return redirect("create-invoice")  # or wherever you want to land post-PRG
    else:
        form = InvoiceForm(request.GET or None)

    # --- Build WIP list for current selection (works for GET and invalid POST) ---
    # Start from a base queryset so we don't lose results when only 'matter' is set.
    cid = form.data.get("client") or None
    mid = form.data.get("matter") or None

    wip_qs = (WIP.objects
            .select_related(
                "matter", "matter__client", "fee_earner", "activity_code")
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
    # --- Filters from GET ---
    number = (request.GET.get("number") or "").strip()
    client = (request.GET.get("client") or "").strip()
    matter = (request.GET.get("matter") or "").strip()
    status = (request.GET.get("status") or "").strip()        # comes from Ledger.status
    date_from = parse_date(request.GET.get("date_from") or "")
    date_to   = parse_date(request.GET.get("date_to") or "")

    filters = {
        "number": number,
        "client": client,
        "matter": matter,
        "status": status,
        "date_from": request.GET.get("date_from") or "",
        "date_to": request.GET.get("date_to") or "",
    }

    # --- Base queryset ---
    qs = (
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .prefetch_related("lines")           # used if you need per-invoice sums
        .order_by("-created_at")
    )

    # --- Apply filters safely ---
    if number:
        qs = qs.filter(number__icontains=number)
    if client:
        qs = qs.filter(client_id=client)
    if matter:
        qs = qs.filter(matter_id=matter)
    if status:
        # filter via related Ledger.status
        qs = qs.filter(ledger__status=status)
    if date_from:
        qs = qs.filter(invoice_date__gte=date_from)
    if date_to:
        qs = qs.filter(invoice_date__lte=date_to)

    # --- Dropdown data ---
    clients = Client.objects.order_by("name")
    # You can narrow matters by client if selected; else show all
    if client:
        matters = Matter.objects.filter(
            client_id=client).order_by("matter_number")
    else:
        matters = Matter.objects.order_by(
            "matter_number")[:500]  # cap to avoid huge lists

    # --- Pagination ---
    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # --- Page totals (fallback to Invoice computed props if no Ledger) ---
    page_subtotal = Decimal("0.00")
    page_tax = Decimal("0.00")
    page_total = Decimal("0.00")
    for inv in page_obj.object_list:
        if getattr(inv, "ledger", None):
            page_subtotal += inv.ledger.subtotal
            page_tax      += inv.ledger.tax
            page_total    += inv.ledger.total
        else:
            page_subtotal += inv.subtotal
            page_tax      += inv.tax_amount
            page_total    += inv.total

    return render(request, "better_bill_project/view_invoice.html", {
        "page_obj": page_obj,
        "filters": filters,
        "clients": clients,
        "matters": matters,
        "page_subtotal": page_subtotal,
        "page_tax": page_tax,
        "page_total": page_total,
    })

@login_required
@permission_required(
    "better_bill_project.post_invoice", raise_exception=True)
def post_invoice_view(request):
    """
    Partners can:
      - POST a draft invoice
      -> ledger.status = 'posted'
      - DELETE a draft invoice
      -> remove invoice & ledger, and revert WIP lines to 'unbilled'
    """
    if request.method == "POST":
        action = request.POST.get("action")
        pk = request.POST.get("invoice_id")
        invoice = get_object_or_404(
            Invoice.objects.select_related("ledger"), pk=pk)

        if action == "post":
            if not invoice.ledger:
                messages.error(
                    request, "Invoice has no ledger; cannot post.",
                    extra_tags="invoice")
                return redirect("post-invoice")
            if invoice.ledger.status == "posted":
                messages.info(
                    request, "Invoice is already posted.", extra_tags="invoice")
                return redirect("post-invoice")

            invoice.ledger.status = "posted"
            invoice.ledger.save(update_fields=["status"])
            messages.success(
                request, f"Invoice {invoice.number} posted.", extra_tags="invoice")
            return redirect("post-invoice")

        elif action == "delete":
            # Only allow delete while draft
            if not invoice.ledger or invoice.ledger.status != "draft":
                messages.error(
                    request, "Only draft invoices can be deleted.",
                    extra_tags="invoice")
                return redirect("post-invoice")

            with transaction.atomic():
                # Revert any WIP used by its lines back to 'unbilled'
                wip_ids = list(invoice.lines.values_list("wip_id", flat=True))
                if wip_ids:
                    WIP.objects.filter(id__in=wip_ids).update(status="unbilled")
                # Deleting invoice will cascade delete lines;
                # OneToOne ledger will be deleted too
                invoice.delete()
            messages.success(
                request, "Draft invoice deleted and WIP reverted to unbilled.",
                extra_tags="invoice")
            return redirect("post-invoice")

        else:
            messages.error(request, "Unknown action.", extra_tags="invoice")
            return redirect("post-invoice")

    # GET: list draft + posted with totals
    drafts = (
        Invoice.objects.select_related("client", "ledger")
        .filter(ledger__status="draft")
        .order_by("-created_at")
    )
    posted = (
        Invoice.objects.select_related("client", "ledger")
        .filter(ledger__status="posted")
        .order_by("-created_at")
    )
    draft_totals = drafts.aggregate(
        subtotal=Sum("ledger__subtotal"),
        tax=Sum("ledger__tax"),
        total=Sum("ledger__total")
    )
    posted_totals = posted.aggregate(
        subtotal=Sum("ledger__subtotal"),
        tax=Sum("ledger__tax"),
        total=Sum("ledger__total")
    )

    return render(request, "better_bill_project/post_invoice.html", {
        "drafts": drafts,
        "posted": posted,
        "draft_total": draft_totals["total"] or Decimal("0.00"),
        "posted_total": posted_totals["total"] or Decimal("0.00"),
    })

# Invoice Detail View
@login_required
def invoice_detail(request, pk):
    inv = get_object_or_404(
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .prefetch_related(
            "lines",
            "lines__wip",
            "lines__wip__fee_earner",
            "lines__wip__activity_code"
        ),
        pk=pk
    )

    # Fallbacks if, for any reason, a ledger doesn't exist
    subtotal = inv.ledger.subtotal if getattr(inv, "ledger", None) else inv.subtotal
    tax      = inv.ledger.tax      if getattr(inv, "ledger", None) else inv.tax_amount
    total    = inv.ledger.total    if getattr(inv, "ledger", None) else inv.total
    status   = inv.ledger.status   if getattr(inv, "ledger", None) else "—"

    return render(request, "better_bill_project/invoice_detail.html", {
        "inv": inv,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "status": status,
    })


# PDF generation view 
@login_required
def invoice_pdf(request, pk):
    inv = get_object_or_404(
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .prefetch_related("lines", "lines__wip", "lines__wip__fee_earner", "lines__wip__activity_code"),
        pk=pk
    )

    subtotal = inv.ledger.subtotal if getattr(inv, "ledger", None) else inv.subtotal
    tax      = inv.ledger.tax      if getattr(inv, "ledger", None) else inv.tax_amount
    total    = inv.ledger.total    if getattr(inv, "ledger", None) else inv.total
    status   = inv.ledger.status   if getattr(inv, "ledger", None) else "draft"

    html = render_to_string("better_bill_project/invoice_pdf.html", {
        "inv": inv, "subtotal": subtotal, "tax": tax, "total": total, "status": status,
    }, request=request)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Base URL lets relative links (e.g. {% static %}) resolve if you use absolute paths in the template
        page.set_content(html, wait_until="load")
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top":"18mm","right":"15mm","bottom":"18mm","left":"15mm"})
        browser.close()

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="Invoice-{inv.number}.pdf"'
    return resp

def custom_404(request, exception):
    return render(
        request, "errors/404.html", {"marker": "USING CUSTOM 404"}, status=404)
