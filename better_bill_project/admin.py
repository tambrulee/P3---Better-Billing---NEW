# Register your models here.

from django.contrib import admin
from .models import Client, Personnel, Matter, TimeEntry

from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username="YOUR_USERNAME")
u.is_staff, u.is_superuser   # should both be True
# if not:
u.is_staff = True
u.is_superuser = True
u.save()
exit()


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_number", "name", "phone", "contact")
    
@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ("initials", "name", "role", "rate")
    
@admin.register(Matter)
class MatterAdmin(admin.ModelAdmin):
    list_display = ("matter_number", "client", "lead_fee_earner", "opened_at", "closed_at")
    
@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("matter", "fee_earner", "hours_worked", "personnel_rate", "total_amount", "activity_code", "created_at")
    