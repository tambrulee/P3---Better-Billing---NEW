from .models import Invoice, Personnel
from .permissions import Scope

ROLE_BILLING = {"billing administrator", "billing", "accounts", "finance"}
ROLE_PARTNER = {"partner"}
ROLE_ASSOC_PARTNER = {"associate partner", "assoc partner", "associate_partner"}

APP_LABEL = Invoice._meta.app_label
PERM_VIEW_INV = f"{APP_LABEL}.view_invoice"

def personnel(request):
    if not request.user.is_authenticated:
        return {"me": None}
    try:
        p = Personnel.objects.select_related("role").get(user=request.user)
    except Personnel.DoesNotExist:
        p = None
    return {"me": p}


def ui_flags(request):
    me = getattr(getattr(request, "user", None), "personnel_profile", None)
    can_view_invoices = False
    if me:
        can_view_invoices = Scope(me).can_view_invoice()
    return {"can_view_invoices": can_view_invoices}

def _personnel(user):
    return getattr(user, "personnel_profile", None)

def _role_name(p) -> str:
    return (getattr(getattr(p, "role", None), "role", "") or "").strip().lower()

def _scope_can_view(user) -> bool:
    p = _personnel(user)
    if not p:
        return False
    rn = _role_name(p)
    is_billing = rn in ROLE_BILLING or ("billing" in rn)
    is_partner = rn in ROLE_PARTNER
    is_assoc  = rn in ROLE_ASSOC_PARTNER
    return any([user.is_superuser, is_billing, is_partner, is_assoc])

def caps(request):
    user = getattr(request, "user", None)
    can_view = False
    if user and user.is_authenticated:
        can_view = user.is_superuser or user.has_perm(
            PERM_VIEW_INV) or _scope_can_view(user)
    return {"can_view_invoices": can_view}


