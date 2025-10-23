from .models import Personnel

def personnel(request):
    if not request.user.is_authenticated:
        return {"me": None}
    try:
        p = Personnel.objects.select_related("role").get(user=request.user)
    except Personnel.DoesNotExist:
        p = None
    return {"me": p}
