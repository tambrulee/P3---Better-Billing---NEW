# better_bill_project/context_processors.py
from .models import Personnel
from .views import can_view_invoices_user, is_time_entry_user

def personnel(request):
    """Add the Personnel profile of the logged-in user to the context."""
    if not getattr(request.user, "is_authenticated", False):
        return {"me": None}
    try:
        p = Personnel.objects.select_related("role").get(user=request.user)
    except Personnel.DoesNotExist:
        p = None
    return {"me": p}

def global_perms(request):
    """
    Global UI flags:
      - can_view_invoices_nav: controls the Invoices tab in the navbar
      - can_record_hours_nav: hides 'Record Hours' for admin and billing
    NOTE: Do NOT return 'can_view_invoices' here; the dashboard already
          sets a page-scoped 'can_view_invoices' in its context.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"can_view_invoices_nav": False, "can_record_hours_nav": False}

    return {
        "can_view_invoices_nav": can_view_invoices_user(user),
        "can_record_hours_nav": is_time_entry_user(user),
    }
