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
    client = models.ForeignKey("Client", on_delete=models.PROTECT, related_name="time_entries")  # NEW
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
