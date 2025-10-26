from .models import Personnel
from .permissions import Scope

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

