from django.db import models
from django.core.validators import MinValueValidator




# --- Client lookup ---
class Client(models.Model):
    client_number =  models.CharField(max_length=6, unique=True)
    name          = models.CharField(max_length=100)
    address       = models.CharField(max_length=100)
    phone         = models.CharField(max_length=50)
    contact       = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.client_number} - {self.name}"


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
    matter         = models.ForeignKey(Matter, on_delete=models.PROTECT, related_name="time_entries")
    fee_earner     = models.ForeignKey(Personnel, on_delete=models.PROTECT, related_name="time_entries")
    personnel_rate = models.DecimalField(max_digits=10, decimal_places=2)
    hours_worked   = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2)
    activity_code  = models.ForeignKey(ActivityCode, on_delete=models.PROTECT,
                                       related_name="time_entries", null=True, blank=True)
    narrative      = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.matter.matter_number} | {self.fee_earner.initials} | {self.hours_worked}h"

