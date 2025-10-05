from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from import_export.admin import ImportExportModelAdmin
from .models import Client, Personnel, Matter, TimeEntry

# --- Resources ---
class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        fields = ("id", "client_number", "name", "address", "phone", "contact")
        import_id_fields = ("client_number",)  # allow updates by client_number

class PersonnelResource(resources.ModelResource):
    class Meta:
        model = Personnel
        fields = ("id", "initials", "name", "rate", "role")
        import_id_fields = ("initials",)  # allow updates by initials

class MatterResource(resources.ModelResource):
    client = fields.Field(
        column_name="client_number",
        attribute="client",
        widget=ForeignKeyWidget(Client, "client_number"),
    )
    lead_fee_earner = fields.Field(
        column_name="lead_fee_earner_initials",
        attribute="lead_fee_earner",
        widget=ForeignKeyWidget(Personnel, "initials"),
    )
    opened_at = fields.Field(
        column_name="opened_at",
        attribute="opened_at",
        widget=DateTimeWidget(format="%Y-%m-%d %H:%M:%S"),
    )
    closed_at = fields.Field(
        column_name="closed_at",
        attribute="closed_at",
        widget=DateTimeWidget(format="%Y-%m-%d %H:%M:%S"),
    )

    class Meta:
        model = Matter
        fields = (
            "id", "matter_number", "description",
            "client", "lead_fee_earner", "opened_at", "closed_at"
        )
        import_id_fields = ("matter_number",)

class TimeEntryResource(resources.ModelResource):
    matter = fields.Field(
        column_name="matter_number",
        attribute="matter",
        widget=ForeignKeyWidget(Matter, "matter_number"),
    )
    fee_earner = fields.Field(
        column_name="fee_earner_initials",
        attribute="fee_earner",
        widget=ForeignKeyWidget(Personnel, "initials"),
    )
    created_at = fields.Field(
        column_name="created_at",
        attribute="created_at",
        widget=DateTimeWidget(format="%Y-%m-%d %H:%M:%S"),
    )

    class Meta:
        model = TimeEntry
        fields = (
            "id", "matter", "fee_earner", "personnel_rate",
            "hours_worked", "total_amount", "activity_code",
            "narrative", "created_at"
        )
        # If you want to allow updating existing rows, add import_id_fields with a natural key.

# --- Admin registrations ---
@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    resource_class = ClientResource
    list_display = ("client_number", "name", "phone", "contact")
    search_fields = ("client_number", "name", "phone", "contact")

@admin.register(Personnel)
class PersonnelAdmin(ImportExportModelAdmin):
    resource_class = PersonnelResource
    list_display = ("initials", "name", "rate", "role")
    search_fields = ("initials", "name", "role")

@admin.register(Matter)
class MatterAdmin(ImportExportModelAdmin):
    resource_class = MatterResource
    list_display = ("matter_number", "client", "lead_fee_earner", "opened_at", "closed_at")
    search_fields = ("matter_number", "description", "client__name", "lead_fee_earner__initials")

@admin.register(TimeEntry)
class TimeEntryAdmin(ImportExportModelAdmin):
    resource_class = TimeEntryResource
    list_display = ("matter", "fee_earner", "hours_worked", "total_amount", "created_at")
    search_fields = ("matter__matter_number", "fee_earner__initials", "activity_code", "narrative")
