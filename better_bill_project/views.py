import os # for path manipulations
from decimal import Decimal # for precise decimal arithmetic
from django.utils import timezone # for timezone-aware date/time
from django.core.paginator import Paginator # for paginating querysets
from django.utils.dateparse import parse_date # for parsing date strings
from django.db.models import Sum # for aggregations
from django.shortcuts import render, redirect, get_object_or_404 # common shortcuts
from io import BytesIO # for in-memory byte streams
from django.conf import settings # for accessing project settings
from django.http import HttpResponse, HttpResponseServerError # for HTTP responses
from django.contrib import messages # for user messages
from django.urls import reverse # for URL reversing
from django.template.loader import render_to_string # for rendering templates to strings
from .forms import TimeEntryForm, InvoiceForm, TimeEntryQuickEditForm # custom forms
from .models import TimeEntry, Client, Matter, ALLOWED_MANAGER_ROLES
from .models import WIP, Invoice, InvoiceLine, Ledger, Personnel, ActivityCode
from django.db.models import Exists, OuterRef # for complex queries
from django.db import transaction # for atomic transactions
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST # for HTTP method restriction
from django.contrib.staticfiles import finders # for static file finding
from urllib.parse import urlparse # for URL parsing
from xhtml2pdf import pisa # for PDF generation

def _p(user):
    """Return Personnel profile for user, or None if not found."""
    return getattr(user, "personnel_profile", None)

def is_cashier(user):
    """Return True if user is cashier."""
    p = _p(user)
    return bool(p and p.is_cashier)

def is_partner(user):
    """Return True if user is partner."""
    p = _p(user)
    return bool(p and p.is_partner)


def is_assoc(user):
    """Return True if user is associate partner."""
    p = _p(user)
    return bool(p and p.is_associate_partner)


def is_billing(user):
    """Return True if user is billing administrator."""
    p = _p(user)
    return bool(p and p.is_billing)


def is_partner_or_assoc(user):
    """Return if user is partner or associate"""
    # Partner or Associate Partner only (Admin excluded)
    return is_partner(user) or is_assoc(user)


def is_view_invoices(user):
    """
    Sets permission for view invoices
    """
    # Associate Partner, Partner, or Billing (Admin excluded)
    return any((
        is_partner(user),
        is_assoc(user),
        is_billing(user),
    ))

def is_time_entry_user(user) -> bool:
    """Allowed to log time = not admin, not billing."""
    if getattr(user, "is_superuser", False):
        return False  # admin cannot record hours
    p = _personnel(user)
    if not p:
        return False
    # treat any 'billing' role as not allowed to record time
    if _is_billing(p):
        return False
    if getattr(p, "is_cashier", False):
        return False
    return True



# --- Permission strings ---
APP_LABEL = Invoice._meta.app_label
PERM_VIEW_INV = f"{APP_LABEL}.view_invoice"
PERM_POST_INV = f"{APP_LABEL}.post_invoice"
PERM_CREATE_INV = f"{Invoice._meta.app_label}.create_invoice"


# -- Views --

# Dashboard View

# Roles allowed to see their team’s WIP and invoices
WIP_ONLY_ROLES = ("Case administrator", "Trainee associate", "Paralegal")

# Helper to check if user can view invoices
ROLE_BILLING = {"billing administrator"}
ROLE_PARTNER = {"partner"}
ROLE_ASSOC_PARTNER = {"associate partner"}

# ---- Role utilities ----
def _personnel(user):
    """Return the Personnel object for a user, regardless of related_name."""
    if not getattr(user, "is_authenticated", False):
        return None
    for rel in ("personnel_profile", "personnel", "profile"):
        p = getattr(user, rel, None)
        if p is not None:
            return p
    try:
        return Personnel.objects.select_related("role").filter(user=user).first()
    except Exception:
        return None

def _role_name(p) -> str:
    """Return the Personnel's role name in lowercase, or empty string."""
    return (getattr(getattr(p, "role", None), "role", "") or "").strip().lower()

def _is_billing(p) -> bool:
    """Return True if Personnel is billing administrator or similar."""
    rn = _role_name(p)
    return rn == "billing administrator" or "billing" in rn or rn in {
        "accounts", "finance"}

def _is_partner(p) -> bool:
    """Return True if Personnel is partner."""
    return _role_name(p) == "partner"

def _is_assoc(p) -> bool:
    """Return True if Personnel is associate partner."""
    return _role_name(p) in {"associate partner"}

def _is_admin(user, p=None) -> bool:
    """Return True if Personnel is admin."""
    # Treat Django superuser as admin
    return bool(getattr(user, "is_superuser", False))

# --- Permission checkers for view invoice tab ----

def can_view_invoices_user(user) -> bool:
    """Only Admin, Billing, Partner,
    Associate Partner can see invoices (not fee earners)."""
    if getattr(user, "is_superuser", False):
        return True

    p = _personnel(user)
    if not p:
        return False

    # Explicit, no cashier references
    if _is_billing(p) or _is_partner(p) or _is_assoc(p):
        return True

    # Everyone else (fee earners etc.) -> no
    return False


# ---- Robust flag resolver ----
BILLING_KEYWORDS = {"billing administrator",}
MANAGER_KEYWORDS = {"partner", "associate partner"}

def _effective_flags(user):
    """
    Returns flags dict:
      - can_view_invoices:
      True for superuser, users with view perm, Personnel boolean flags,
      or role names containing billing/manager keywords.
      - can_log_time: False for billing/cashier;
      True otherwise (if Personnel exists).
      Works even if your Personnel booleans aren't set,
      by falling back to role name keywords.
    """
    flags = {"can_view_invoices": False, "can_log_time": False}
    if not getattr(user, "is_authenticated", False):
        return flags

    # Superuser is always allowed
    if getattr(user, "is_superuser", False):
        flags["can_view_invoices"] = True
        flags["can_log_time"] = False  # admin can’t record hours
        return flags


    # Permission fallback (keep if you've set perms)
    try:
        if user.has_perm(PERM_VIEW_INV):
            flags["can_view_invoices"] = True
    except Exception:
        pass

    p = _personnel(user)
    if not p:
        return flags

    # Pull booleans if your Personnel has them; default to False if missing
    p_is_admin   = bool(getattr(p, "is_admin", False))
    p_is_billing = bool(getattr(p, "is_billing", False))
    p_is_cashier = bool(getattr(p, "is_cashier", False))
    p_is_partner = bool(getattr(p, "is_partner", False))
    p_is_assoc   = bool(getattr(p, "is_associate_partner", False))

    # Role name tolerance
    rn = _role_name(p)  # already lower-cased in your helper
    # quick keyword tests
    has_billing_kw = any(k in rn for k in BILLING_KEYWORDS)
    is_manager_kw  = any(k in rn for k in MANAGER_KEYWORDS)

    # Compute
    can_view = (
        flags["can_view_invoices"]                # from perms above, if any
        or p_is_admin or p_is_billing or p_is_cashier or p_is_partner or p_is_assoc
        or has_billing_kw or is_manager_kw
    )
    # Time logging: block billing/cashier (by boolean or keyword)
    is_billingish = p_is_billing or p_is_cashier or has_billing_kw
    can_log = not is_billingish

    flags["can_view_invoices"] = bool(can_view)
    flags["can_log_time"] = bool(can_log)
    return flags


def _team_personnel_ids(me: Personnel | None):
    """
    Return None => no filtering (see all).
    Return []   => filter but matches nothing (guest).
    Return [ids] => filter to these fee earners.
    """
    if not me:
        return []
    # Admin or Billing => see everything
    if getattr(me, "is_admin", False) or _is_billing(me):
        return None

    ids = [me.id]
    rn = _role_name(me)
    if rn in ALLOWED_MANAGER_ROLES:
        try:
            ids += list(me.delegates.values_list("id", flat=True))
        except Exception:
            pass
    return ids

def require_invoice_access(viewfunc):
    """Decorator to require invoice view permission."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        """Check permission before calling view."""
        if not can_view_invoices_user(request.user):
            raise PermissionDenied
        return viewfunc(request, *args, **kwargs)
    return _wrapped

def _is_billing_only(user):
    """True only for Billing role (plus superuser override)."""
    if getattr(user, "is_superuser", False):
        return True
    p = _personnel(user)
    return bool(p) and _is_billing(p)


# Index

@login_required
def index(request):
    """ Dashboard view showing WIP and invoices based on roles/permissions. """
    me = _personnel(request.user)

    p = me
    rn = _role_name(p) if p else "<none>"
    info = {
        "is_superuser": bool(getattr(request.user, "is_superuser", False)),
        "p_exists": bool(p),
        "p_is_admin": bool(getattr(p, "is_admin", False)) if p else False,
        "p_is_billing": bool(getattr(p, "is_billing", False)) if p else False,
        "p_is_cashier": bool(getattr(p, "is_cashier", False)) if p else False,
        "p_is_partner": bool(getattr(p, "is_partner", False)) if p else False,
        "p_is_assoc": bool(getattr(p, "is_associate_partner", False)) if p else False,
        "role_name": rn,
    }
    print("DASHBOARD ROLES:", info)  # shows up in runserver console

    context = {
        "wip_items": [],
        "wip_total_hours": Decimal("0.0"),
        "draft_invoices": [],
        "draft_subtotal": Decimal("0.00"),
        "draft_tax":      Decimal("0.00"),
        "draft_total":    Decimal("0.00"),
        "posted_invoices": [],
        "post_subtotal":  Decimal("0.00"),
        "post_tax":       Decimal("0.00"),
        "post_total":     Decimal("0.00"),
        "can_view_invoices": False,
        "can_log_time": False,
    }

    if not me:
        return render(request, "better_bill_project/index.html", context)

    flags = _effective_flags(request.user)
    context["can_view_invoices"] = flags["can_view_invoices"]
    context["can_log_time"] = flags["can_log_time"]

    # ----- Team scoping -----
    team_ids = _team_personnel_ids(me)  # may be None, [], or [ids]
    # Admin/Billing see everything (clear filter)
    if getattr(request.user, "is_superuser", False) or any(
        k in _role_name(me) for k in BILLING_KEYWORDS) or getattr(
            me, "is_admin", False) or getattr(me, "is_billing", False):
        team_ids = None

    # ----- Unbilled WIP -----
    wip_qs = (WIP.objects
              .select_related("matter", "client")
              .filter(status="unbilled")
              .order_by("-created_at"))
    if team_ids:
        wip_qs = wip_qs.filter(fee_earner_id__in=team_ids)

    context["wip_items"] = list(wip_qs[:10])
    context["wip_total_hours"] = wip_qs.aggregate(
        total=Sum("hours_worked"))["total"] or Decimal("0.0")

    # ----- Invoices (only when allowed) -----
    if context["can_view_invoices"]:
        invoice_base = (Invoice.objects
                        .select_related("client", "matter", "ledger"))

        if team_ids:
            invoice_base = (invoice_base
                .annotate(has_team_work=Exists(
                    InvoiceLine.objects.filter(
                        invoice_id=OuterRef("pk"),
                        wip__fee_earner_id__in=team_ids
                    )
                ))
                .filter(has_team_work=True))

        draft_qs  = invoice_base.filter(
            ledger__status="draft").order_by("-created_at")[:10]
        posted_qs = invoice_base.filter(
            ledger__status="posted").order_by("-created_at")[:10]

        draft_totals = draft_qs.aggregate(
            subtotal=Sum("ledger__subtotal"),
            tax=Sum("ledger__tax"), total=Sum("ledger__total"))
        post_totals  = posted_qs.aggregate(
            subtotal=Sum("ledger__subtotal"),
            tax=Sum("ledger__tax"), total=Sum("ledger__total"))

        context.update({
            "draft_invoices": list(draft_qs),
            "draft_subtotal": draft_totals["subtotal"] or Decimal("0.00"),
            "draft_tax":      draft_totals["tax"]      or Decimal("0.00"),
            "draft_total":    draft_totals["total"]    or Decimal("0.00"),
            "posted_invoices": list(posted_qs),
            "post_subtotal":  post_totals["subtotal"]  or Decimal("0.00"),
            "post_tax":       post_totals["tax"]       or Decimal("0.00"),
            "post_total":     post_totals["total"]     or Decimal("0.00"),
        })

    return render(request, "better_bill_project/index.html", context)

# Time Entry Form
@login_required
@user_passes_test(is_time_entry_user,
                  login_url="/errors/403.html")  # redirects if not allowed
def record_time(request):
    """ View for recording time entries and listing recent entries. """
    def _is_partner_or_assoc_user(u):
        if getattr(u, "is_superuser", False):
            return True
        p = _personnel(u)
        if not p:
            return False
        return _is_partner(p) or _is_assoc(p)

    is_partner = _is_partner_or_assoc_user(request.user)

    fe_filter = request.GET.get("fe")
    personnel_for_user = getattr(
        request.user, "personnel_profile", None)

    base_qs = (TimeEntry.objects
               .select_related("matter", "fee_earner", "wip")
               .order_by("-created_at"))

    if is_partner:
        if fe_filter:
            base_qs = base_qs.filter(fee_earner_id=fe_filter)
        fee_earners = Personnel.objects.order_by("name")
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
        form = TimeEntryForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Time entry saved.")
            return redirect("record-time")
        else:
            messages.error(request, "Please correct the errors below.")
        form_qe = None
    else:
        form = TimeEntryForm(user=request.user)
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
@user_passes_test(is_time_entry_user,
                  login_url="/errors/403.html")  # redirects if not allowed
def delete_time_entry(request, pk):
    """ Delete a time entry if unbilled and permitted.
    """

    def _is_partner_or_assoc_user(u):
        if getattr(u, "is_superuser", False):
            return True
        p = _personnel(u)
        if not p:
            return False
        return _is_partner(p) or _is_assoc(p)

    is_partner = _is_partner_or_assoc_user(request.user)

    personnel_for_user = getattr(request.user, "personnel_profile", None)

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
    """ Given a client ID in GET, return HTML options for that client's open matters."""
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

@login_required
def create_invoice(request):
    """ Create an invoice from selected unbilled WIP items.
    """
    readonly_number = _next_invoice_number()
    readonly_date = timezone.localdate()
    readonly_tax = Decimal("20.00")  # percent

    if request.method == "POST":
        form = InvoiceForm(request.POST, user=request.user)
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
        form = InvoiceForm(request.GET, user=request.user or None)

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
@login_required
@require_invoice_access
def view_invoice(request):
    """ List and filter invoices with pagination and totals.
    """
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
@permission_required(PERM_POST_INV, raise_exception=True)
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
@require_invoice_access
def invoice_detail(request, pk):
    """ View details of a single invoice, with billing controls if allowed. """
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

    has_ledger = getattr(inv, "ledger", None) is not None
    ledger = inv.ledger if has_ledger else None

    # Fallbacks if no ledger exists
    subtotal = ledger.subtotal if has_ledger else inv.subtotal
    tax      = ledger.tax      if has_ledger else inv.tax_amount
    total    = ledger.total    if has_ledger else inv.total
    status   = ledger.status   if has_ledger else "—"

    # ---- Billing-only controls ----
    is_billing_user = _is_billing_only(request.user)
    can_settle   = bool(is_billing_user and has_ledger and ledger.status == "posted")
    can_unsettle = bool(is_billing_user and has_ledger and ledger.status == "paid")

    return render(request, "better_bill_project/invoice_detail.html", {
        "inv": inv,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "status": status,
        "can_settle": can_settle,
        "can_unsettle": can_unsettle,
    })


# PDF Viewer

def _xhtml2pdf_link_callback(uri, rel):
    """
    Resolve static/media URIs for xhtml2pdf.
    Supports:
      - /static/... (Django staticfiles)
      - /media/...  (user uploads)
      - absolute http(s) URLs (leave as-is; xhtml2pdf can fetch some)
    """
    parsed = urlparse(uri)
    if parsed.scheme in ("http", "https"):
        return uri  # allow remote if needed (or block if you prefer)
    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, "", 1)
        abs_path = finders.find(path)  # in collected static or app dirs
        if abs_path:
            return abs_path
    if uri.startswith(settings.MEDIA_URL):
        path = uri.replace(settings.MEDIA_URL, "", 1)
        return os.path.join(settings.MEDIA_ROOT, path)
    return uri

# PDF generation view
@login_required
@require_invoice_access
def invoice_pdf(request, pk):
    """ Render an invoice as PDF and return as HTTP response."""
    inv = get_object_or_404(
        Invoice.objects
        .select_related("client", "matter", "ledger")
        .prefetch_related("lines", "lines__wip",
                          "lines__wip__fee_earner", "lines__wip__activity_code"),
        pk=pk
    )

    subtotal = inv.ledger.subtotal if getattr(inv, "ledger", None) else inv.subtotal
    tax      = inv.ledger.tax      if getattr(inv, "ledger", None) else inv.tax_amount
    total    = inv.ledger.total    if getattr(inv, "ledger", None) else inv.total
    status   = inv.ledger.status   if getattr(inv, "ledger", None) else "draft"

    html = render_to_string(
        "better_bill_project/invoice_pdf.html",
        {"inv": inv, "subtotal": subtotal, "tax": tax, "total": total,
         "status": status},
        request=request,
    )

    # ensure relative links work (static/css/images)
    base_href = request.build_absolute_uri("/")
    html = html.replace("<head>", f'<head><base href="{base_href}">', 1)

    # Render HTML -> PDF
    pdf_io = BytesIO()
    result = pisa.CreatePDF(
        src=html,
        dest=pdf_io,
        encoding="utf-8",
        link_callback=_xhtml2pdf_link_callback,
    )
    if result.err:

        return HttpResponseServerError("PDF render failed.")

    pdf_bytes = pdf_io.getvalue()
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="Invoice-{inv.number}.pdf"'
    return resp

# Settle Invoice View
@login_required
@permission_required(PERM_POST_INV, raise_exception=True)  # was PERM_VIEW_INV
@require_POST
@transaction.atomic
def settle_invoice(request, pk):
    """ Mark an invoice as settled (paid) if posted."""
    if not _is_billing_only(request.user):
        raise PermissionDenied

    invoice = get_object_or_404(Invoice.objects.select_related("ledger"), pk=pk)
    ledger = getattr(invoice, "ledger", None)
    if ledger is None:
        messages.error(request, "No ledger entry exists for this invoice.")
        return redirect("invoice-detail", pk=pk)

    if ledger.status != "posted":
        messages.error(request, "Only posted invoices can be settled.")
        return redirect("invoice-detail", pk=pk)

    # Idempotency
    if ledger.status == "paid":
        messages.info(request, "This invoice is already marked as paid.")
        return redirect("invoice-detail", pk=pk)

    ledger.status = "paid"
    ledger.paid_at = timezone.now()
    ledger.save(update_fields=["status", "paid_at"])

    messages.success(request, f"Invoice {invoice.number} marked as settled.")
    return redirect("invoice-detail", pk=pk)


# Unsettle Invoice View
@login_required                         # <— add this (was missing)
@permission_required(PERM_POST_INV, raise_exception=True)  # was PERM_VIEW_INV
@require_POST
@transaction.atomic
def unsettle_invoice(request, pk):
    """ Unmark an invoice as settled (paid) if previously paid."""
    if not _is_billing_only(request.user):
        raise PermissionDenied

    invoice = get_object_or_404(Invoice.objects.select_related("ledger"), pk=pk)
    ledger = getattr(invoice, "ledger", None)
    if ledger is None:
        messages.error(request, "No ledger entry exists for this invoice.")
        return redirect("invoice-detail", pk=pk)

    if ledger.status != "paid":
        messages.error(request, "Only paid invoices can be unmarked as settled.")
        return redirect("invoice-detail", pk=pk)

    ledger.status = "posted"
    ledger.paid_at = None
    ledger.save(update_fields=["status", "paid_at"])

    messages.success(request, f"Invoice {invoice.number} unmarked as settled.")
    return redirect("invoice-detail", pk=pk)


# Custom 404 page

def custom_404(request, exception):
    """ Custom 404 error handler."""
    return render(
        request, "errors/404.html", {"marker": "USING CUSTOM 404"}, status=404)
