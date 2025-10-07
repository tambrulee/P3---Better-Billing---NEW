from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import TimeEntry, Matter, Personnel, ActivityCode

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["matter", "fee_earner", "activity_code", "hours_worked", "narrative"]
        widgets = {
            "matter": forms.Select(attrs={"class": "form-select"}),
            "fee_earner": forms.Select(attrs={"class": "form-select"}),
            "activity_code": forms.Select(attrs={"class": "form-select"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "0"}),
            "narrative": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_hours_worked(self):
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        if (Decimal(value) * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
