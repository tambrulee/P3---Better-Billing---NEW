# forms.py
from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import TimeEntry, Matter, Personnel, ActivityCode, Client, WIP, Invoice

# Time entry form with dynamic matter filtering based on selected client

class TimeEntryForm(forms.ModelForm):
    # helper field ONLY for filtering the matters list
    client = forms.ModelChoiceField(
        queryset=Client.objects.order_by("name"),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = TimeEntry
        fields = ["client", "matter", "fee_earner", "activity_code", "hours_worked", "narrative"]
        widgets = {
            "matter": forms.Select(attrs={"class": "form-select"}),
            "fee_earner": forms.Select(attrs={"class": "form-select"}),
            "activity_code": forms.Select(attrs={"class": "form-select"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "0"}),
            "narrative": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

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
            cid = getattr(getattr(self.instance, "matter", None), "client_id", None)

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

    def clean_hours_worked(self):
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        q = Decimal(value)
        if (q * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return q.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    def save(self, commit=True):
        """Save a TimeEntry. WIP creation happens in the view."""
        return super().save(commit=commit)

# Invoice form with dynamic matter filtering 

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
    
# Customized authentication form with Bootstrap styling

from django.contrib.auth.forms import AuthenticationForm

class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})

# Time Editing

class TimeEntryQuickEditForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["hours_worked", "narrative", "activity_code"]
        widgets = {
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "0"}),
            "narrative": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "activity_code": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_hours_worked(self):
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        q = Decimal(value)
        if (q * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return q.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


