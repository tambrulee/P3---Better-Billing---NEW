# forms.py
from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import TimeEntry, Matter, Personnel, ActivityCode, Client, WIP, Invoice

class TimeEntryForm(forms.ModelForm):
    # helper field ONLY for filtering the matters list
    client = forms.ModelChoiceField(
        queryset=Client.objects.order_by("name"),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = WIP   # or TimeEntry if that’s your model
        fields = ["matter", "fee_earner", "hours_worked", "activity_code", "narrative"]  # <-- no 'client'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Narrow matters to the selected client
        cid = None
        data = getattr(self, "data", None)
        if data and data.get("client"):
            try:
                cid = int(data.get("client"))
            except (TypeError, ValueError):
                cid = None
        elif getattr(self.instance, "pk", None):
            # if editing existing, infer from instance.matter
            cid = getattr(getattr(self.instance, "matter", None), "client_id", None)

        if cid:
            self.fields["matter"].queryset = Matter.objects.filter(
                client_id=cid, closed_at__isnull=True
            ).order_by("matter_number")
        else:
            self.fields["matter"].queryset = Matter.objects.none()

    def save(self, commit=True):
        # Strip helper field so it’s not passed to the model
        self.cleaned_data.pop("client", None)
        obj = super().save(commit=False)
        # Ensure all required model fields are set; client comes via obj.matter.client
        if commit:
            obj.save()
        return obj

    def clean_hours_worked(self):
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        if (Decimal(value) * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return Decimal(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)



# forms.py
class InvoiceForm(forms.ModelForm):
    matter = forms.ModelChoiceField(
        queryset=Matter.objects.none(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_inv_matter", "required": True})
    )

    class Meta:
        model = Invoice
        fields = ["client", "matter", "notes"]
        widgets = {
            "client": forms.Select(attrs={"id": "id_inv_client", "class": "form-select", "required": True}),
            "matter": forms.Select(attrs={"id": "id_inv_matter", "class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].required = True
        self.fields["matter"].required = True

        self.fields["client"].queryset = Client.objects.order_by("name")

        cid = None
        data = getattr(self, "data", None)
        if data and data.get("client"):
            try:
                cid = int(data.get("client"))
            except (TypeError, ValueError):
                cid = None
        elif self.instance.pk and self.instance.client_id:
            cid = self.instance.client_id

        if cid:
            self.fields["matter"].queryset = Matter.objects.filter(
                client_id=cid, closed_at__isnull=True
            ).order_by("matter_number")
        else:
            self.fields["matter"].queryset = Matter.objects.none()

    def clean(self):
        cleaned = super().clean()
        client = cleaned.get("client")
        matter = cleaned.get("matter")
        if client and matter and matter.client_id != client.id:
            self.add_error("matter", "Selected matter does not belong to the chosen client.")
        return cleaned

