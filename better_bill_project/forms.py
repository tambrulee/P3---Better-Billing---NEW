# forms.py
from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import TimeEntry, Matter, Personnel, ActivityCode, Client

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["client", "matter", "fee_earner", "activity_code", "hours_worked", "narrative"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select", "id": "id_client"}),
            "matter": forms.Select(attrs={"class": "form-select", "id": "id_matter"}),
            "fee_earner": forms.Select(attrs={"class": "form-select"}),
            "activity_code": forms.Select(attrs={"class": "form-select"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "0"}),
            "narrative": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        help_texts = {"hours_worked": "Enter time in 0.1-hour increments (6 minutes)."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.order_by("name")
        self.fields["matter"].queryset = Matter.objects.none()  # start empty until client chosen
        self.fields["fee_earner"].queryset = Personnel.objects.order_by("initials")
        self.fields["activity_code"].queryset = ActivityCode.objects.order_by("activity_code")
        self.fields["activity_code"].empty_label = "— Select activity (optional) —"

        # If we have data (POST) or an instance (editing), filter matters accordingly
        client_id = None
        if "client" in self.data:
            try:
                client_id = int(self.data.get("client"))
            except (TypeError, ValueError):
                pass
        elif self.instance.pk and self.instance.client_id:
            client_id = self.instance.client_id

        if client_id:
            self.fields["matter"].queryset = (
                Matter.objects.filter(client_id=client_id, closed_at__isnull=True)
                .order_by("matter_number")
            )

    def clean_hours_worked(self):
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        if (Decimal(value) * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return Decimal(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
