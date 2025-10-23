from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from import_export.admin import ImportExportModelAdmin

# IMPORTANT: include Role here
from .models import Client, Personnel, Role, Matter
from .models import TimeEntry, ActivityCode, WIP, Invoice, InvoiceLine, Ledger

# --- Resources ---

class RoleResource(resources.ModelResource):
    class Meta:
        model = Role
        fields = ("id", "role", "rate")
        import_id_fields = ("role",)  # update by role name


class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        fields = ("id", "client_number", "name", "address", "phone", "contact")
        import_id_fields = ("client_number",)


class PersonnelResource(resources.ModelResource):
    # Map FK by Role.role (name) instead of ID for import/export
    role = fields.Field(
        column_name="role",
        attribute="role",
        widget=ForeignKeyWidget(Role, "role"),
    )

    class Meta:
        model = Personnel
        fields = ("id", "initials", "name", "role")
        import_id_fields = ("initials",)


class MatterResource(resources.ModelResource):
    client = fields.Field(
        column_name="client_number",
        attribute="client",
        widget=ForeignKeyWidget(Client, "client_number"),
    )
    lead_fee_earner = fields.Field(
        column_name="lead_fee_earner_name",
        attribute="lead_fee_earner",
        widget=ForeignKeyWidget(Personnel, "name"),
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
        # Add import_id_fields if you later define a natural key


# --- Admin registrations ---

@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    resource_class = RoleResource
    list_display = ("role", "rate")
    search_fields = ("role",)


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    list_display = ("client_number", "name",
                    "city", "county", "postcode", "phone", "contact")
    search_fields = ("client_number", "name",
                    "city", "county", "postcode", "phone", "contact")
    fields = (
        "client_number", "name",
        ("address_line_1", "address_line_2"),
        ("street_name", "city", "county", "postcode"),
        "phone", "contact",
    )



@admin.register(Personnel)
class PersonnelAdmin(ImportExportModelAdmin):
    resource_class = PersonnelResource
    list_display = ("initials", "name", "role", "rate_display", "line_manager")
    list_select_related = ("role",)
    search_fields = ("initials", "name", "role__role","line_manager", "user__username", "user__email")  # note the double underscore
    autocomplete_fields = ["user", "role", "line_manager"]
    def rate_display(self, obj):
        """ Display the rate from the related Role model. """
        return obj.role.rate
    rate_display.short_description = "Rate"
    rate_display.admin_order_field = "role__rate"


@admin.register(Matter)
class MatterAdmin(ImportExportModelAdmin):
    resource_class = MatterResource
    list_display = ("matter_number", "client",
                    "lead_fee_earner", "opened_at", "closed_at")
    list_select_related = ("client", "lead_fee_earner")
    search_fields = ("matter_number", "description",
                     "client__name", "lead_fee_earner__name")

@admin.register(ActivityCode)
class ActivityCodeAdmin(ImportExportModelAdmin):
    list_display = ("activity_code", "activity_description")
    search_fields = ("activity_code", "activity_description")

@admin.register(TimeEntry)
class TimeEntryAdmin(ImportExportModelAdmin):
    resource_class = TimeEntryResource
    list_display = ("matter", "fee_earner", "hours_worked", "created_at")
    list_select_related = ("matter", "fee_earner")
    search_fields = ("matter__matter_number",
                     "fee_earner__initials", "activity_code", "narrative")

@admin.register(WIP)
class WIPAdmin(admin.ModelAdmin):
    list_display = ("created_at", 'client', "matter",
                    "fee_earner", "hours_worked", "status")
    list_filter  = ("status", "fee_earner", "matter", "created_at")
    search_fields = ("matter__matter_number", "fee_earner__initials", "narrative")

# ------ Invoicing ------

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0
    readonly_fields = ("amount",)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "invoice_date", "client",
                    "matter", "tax_rate", "created_at")
    list_filter  = ("client", "matter", "invoice_date")
    search_fields = ("number", "client__name", "matter__matter_number")
    inlines = [InvoiceLineInline]

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ("invoice", "client", "matter", "subtotal",
                    "tax", "total", "status", "created_at")
    list_filter  = ("status", "client", "matter", "created_at")
    search_fields = ("invoice__number", "client__name", "matter__matter_number")

