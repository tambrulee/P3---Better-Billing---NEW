
from django.db import models

# --- Core lookups ---
class Client(models.Model):
    client_number = models.IntegerField(unique=True)
    name          = models.CharField(max_length=255)
    address       = models.TextField(blank=True)
    phone         = models.CharField(max_length=50, blank=True)
    contact       = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.client_number} - {self.name}"


class Personnel(models.Model):
    initials = models.CharField(max_length=10, unique=True)
    name     = models.CharField(max_length=255)
    rate     = models.DecimalField(max_digits=10, decimal_places=2)  # money
    role     = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["initials"]

    def __str__(self):
        return f"{self.initials} - {self.name}"


class Matter(models.Model):
    matter_number   = models.CharField(max_length=50, unique=True)
    description     = models.CharField(max_length=255, blank=True)
    client          = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="matters")
    lead_fee_earner = models.ForeignKey(Personnel, on_delete=models.PROTECT, related_name="lead_matters")
    opened_at       = models.DateTimeField()
    closed_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["matter_number"]

    def __str__(self):
        return f"{self.matter_number} - {self.description or self.client.name}"


# --- Transactions / timecards ---
class TimeEntry(models.Model):
    matter         = models.ForeignKey(Matter, on_delete=models.PROTECT, related_name="time_entries")
    fee_earner     = models.ForeignKey(Personnel, on_delete=models.PROTECT, related_name="time_entries")
    # store the rate used when the entry was recorded, so historical bills don't change
    personnel_rate = models.DecimalField(max_digits=10, decimal_places=2)
    hours_worked   = models.DecimalField(max_digits=8, decimal_places=2)  # e.g. 0.25 increments
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2)
    activity_code  = models.CharField(max_length=50, blank=True)
    narrative      = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.matter.matter_number} | {self.fee_earner.initials} | {self.hours_worked}h"

