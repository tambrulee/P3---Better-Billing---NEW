from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# --- Client lookup ---
class Client(models.Model):
    client_number = models.CharField(max_length=6, unique=True)
    name          = models.CharField(max_length=100)
    
    # Address fields (normalized)
    address_line_1 = models.CharField("Address Line 1", max_length=100, blank=True)
    address_line_2 = models.CharField("Address Line 2", max_length=100, blank=True)
    street_name    = models.CharField("Street Name", max_length=100, blank=True)
    city           = models.CharField("City", max_length=100, blank=True)
    county         = models.CharField("County", max_length=100, blank=True)
    postcode       = models.CharField("Postcode", max_length=20, blank=True)

    phone          = models.CharField(max_length=50, blank=True)
    contact        = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.client_number} - {self.name}"

    @property
    def full_address(self):
        """Combine address components into a single display string."""
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.street_name,
            self.city,
            self.county,
            self.postcode,
        ]
        return ", ".join(p for p in parts if p)



# --- Roles lookup ---

class Role(models.Model):
    role = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["role"]

    def __str__(self):
        return f"{self.role} @ {self.rate}"

# --- Personnel lookup ---

class Personnel(models.Model):
    initials = models.CharField(max_length=10, unique=True)
    name     = models.CharField(max_length=255)
    role     = models.ForeignKey("Role", on_delete=models.PROTECT,
                                 related_name="personnel",
                                 null=True, blank=True)  # TEMP
    class Meta:
        ordering = ["initials"]

    def __str__(self):
        return f"{self.initials} - {self.name} ({self.role.role if self.role_id else self.role_text or '—'})"
 
 # --- Matter lookup ---

class Matter(models.Model):
    matter_number   = models.CharField(max_length=50, unique=True)
    description     = models.CharField(max_length=255)
    client          = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="matters")
    lead_fee_earner = models.ForeignKey(Personnel, on_delete=models.PROTECT, related_name="lead_matters")
    opened_at       = models.DateTimeField()
    closed_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["matter_number"]

    def __str__(self):
        return f"{self.matter_number} - {self.description or self.client.name}"
   
# --- Activity code lookup ---
class ActivityCode(models.Model):
    activity_code        = models.CharField(max_length=50, unique=True)
    activity_description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["activity_code"]
        verbose_name = "Activity Code"
        verbose_name_plural = "Activity Codes"

    def __str__(self):
        return f"{self.activity_code} - {self.activity_description}"

# --- Time Entry ---

class TimeEntry(models.Model):
    client = models.ForeignKey(
    "Client",
    on_delete=models.PROTECT,
    related_name="time_entries",
    null=True, blank=True,   # ← TEMP so the column can be added
)
    matter = models.ForeignKey("Matter", on_delete=models.PROTECT, related_name="time_entries")
    fee_earner = models.ForeignKey("Personnel", on_delete=models.PROTECT, related_name="time_entries")
    activity_code = models.ForeignKey("ActivityCode", on_delete=models.PROTECT,
                                      related_name="time_entries", null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=1,
                                       help_text="Time worked, in 0.1-hour increments (6 minutes)")
    narrative = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        # Ensure the matter selected actually belongs to the chosen client
        if self.matter_id and self.client_id and self.matter.client_id != self.client_id:
            raise ValidationError({"matter": "Selected matter does not belong to the chosen client."})

    def __str__(self):
        return f"{self.matter.matter_number} | {self.fee_earner.initials} | {self.hours_worked}h"

# --- WIP ---

class WIP(models.Model):
    STATUS_CHOICES = [
        ("unbilled", "Unbilled"),
        ("billed", "Billed"),
        ("written_off", "Written off"),
    ]

    time_entry    = models.OneToOneField("TimeEntry", on_delete=models.CASCADE, related_name="wip")
    matter        = models.ForeignKey("Matter", on_delete=models.PROTECT, related_name="wip_items")
    fee_earner    = models.ForeignKey("Personnel", on_delete=models.PROTECT, related_name="wip_items")
    activity_code = models.ForeignKey("ActivityCode", on_delete=models.PROTECT, null=True, blank=True, related_name="wip_items")

    hours_worked  = models.DecimalField(max_digits=5, decimal_places=1)  # mirrors TimeEntry
    narrative     = models.TextField(blank=True)

    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unbilled")
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"WIP for {self.matter.matter_number} | {self.fee_earner.initials} | {self.hours_worked}h ({self.status})"

class Invoice(models.Model):
    number       = models.CharField(max_length=50, unique=True)
    client       = models.ForeignKey("Client", on_delete=models.PROTECT, related_name="invoices")
    matter       = models.ForeignKey("Matter", on_delete=models.PROTECT, related_name="invoices", null=True, blank=True)
    invoice_date = models.DateField()
    notes        = models.TextField(blank=True)
    tax_rate     = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"),
                                       validators=[MinValueValidator(0)])

    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"INV {self.number} — {self.client.name}"

    @property
    def subtotal(self):
        return sum((li.amount for li in self.lines.all()), Decimal("0.00"))

    @property
    def tax_amount(self):
        return (self.subtotal * (self.tax_rate / Decimal("100"))).quantize(Decimal("0.01"))

    @property
    def total(self):
        return (self.subtotal + self.tax_amount).quantize(Decimal("0.01"))


class InvoiceLine(models.Model):
    invoice   = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="lines")
    wip       = models.ForeignKey("WIP", on_delete=models.PROTECT, related_name="invoiced_lines")
    desc      = models.CharField(max_length=255, blank=True)
    hours     = models.DecimalField(max_digits=6, decimal_places=1)
    rate      = models.DecimalField(max_digits=10, decimal_places=2, help_text="Snapshot of rate at invoice time")
    amount    = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.invoice.number} — {self.wip.matter.matter_number} — {self.amount}"


class Ledger(models.Model):
    STATUS = [("draft", "Draft"), ("posted", "Posted")]
    invoice     = models.OneToOneField("Invoice", on_delete=models.CASCADE, related_name="ledger")
    client      = models.ForeignKey("Client", on_delete=models.PROTECT, related_name="ledger_entries")
    matter      = models.ForeignKey("Matter", on_delete=models.PROTECT, related_name="ledger_entries", null=True, blank=True)
    subtotal    = models.DecimalField(max_digits=12, decimal_places=2)
    tax         = models.DecimalField(max_digits=12, decimal_places=2)
    total       = models.DecimalField(max_digits=12, decimal_places=2)
    status      = models.CharField(max_length=10, choices=STATUS, default="draft")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ledger for {self.invoice.number} — {self.total}"
