# forms.py
from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import TimeEntry, Matter, Client, Invoice, Personnel
from django.contrib.auth.forms import AuthenticationForm

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
        fields = [
            "client", "matter", "fee_earner",
            "activity_code", "hours_worked", "narrative"]
        widgets = {
            "matter": forms.Select(attrs={"class": "form-select"}),
            "fee_earner": forms.Select(attrs={"class": "form-select"}),
            "activity_code": forms.Select(attrs={"class": "form-select"}),
            "hours_worked": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0"}),
            "narrative": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # keep a handle to the user for save()
        self._user = user
        me = getattr(user, "personnel_profile", None)
        is_partner = bool(user and (user.has_perm(
            "better_bill_project.post_invoice") or user.is_superuser))

        # ----- default fee_earner to current user -----
        if me:
            self.fields["fee_earner"].initial = me.pk

        # Non-partners: lock the dropdown to themselves
        if me and not is_partner:
            self.fields["fee_earner"].queryset = Personnel.objects.filter(pk=me.pk)
            self.fields["fee_earner"].empty_label = None  # no blank option

        # Clients with at least one OPEN matter
        open_client_ids = (
            Matter.objects
            .filter(closed_at__isnull=True)
            .values_list("client_id", flat=True)
            .distinct()
        )
        clients_with_open_matters = Client.objects.filter(
            id__in=open_client_ids).order_by("name")

        # if editing an instance whose client has no open matters, still include it
        inst_client_id = getattr(getattr(self.instance, "client", None), "id", None)
        if inst_client_id and inst_client_id not in open_client_ids:
            clients_with_open_matters = (
                Client.objects.filter(id=inst_client_id) | clients_with_open_matters
            ).order_by("name")

        self.fields["client"].queryset = clients_with_open_matters

        # ----- existing matter narrowing logic -----
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
            self.fields["matter"].queryset = (
                Matter.objects.filter(client_id=cid, closed_at__isnull=True)
                .order_by("matter_number")
            )
        else:
            self.fields["matter"].queryset = Matter.objects.none()

    def clean(self):
        """ Ensure that the selected matter belongs to the selected client. """
        cleaned = super().clean()
        client = cleaned.get("client")
        matter = cleaned.get("matter")
        if client and matter and matter.client_id != client.id:
            self.add_error(
                "matter", "Selected matter does not belong to the chosen client.")
        # Also ensure matter is not closed
        if matter and matter.closed_at is not None:
            self.add_error("matter", "This matter is closed and cannot be selected.")
        return cleaned

    def clean_hours_worked(self):
        """ Ensure hours worked is in 0.1-hour increments."""
        value = self.cleaned_data.get("hours_worked")
        if value is None:
            return value
        q = Decimal(value)
        if (q * 10) % 1 != 0:
            raise ValidationError("Hours must be in 0.1-hour increments.")
        return q.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    def save(self, commit=True):
        """
        Save a TimeEntry.
        Enforce fee_earner for non-partners (prevents crafted POSTs).
        """
        obj = super().save(commit=False)
        user = getattr(self, "_user", None)
        me = getattr(user, "personnel_profile", None)
        is_partner = bool(user and (
            user.has_perm("better_bill_project.post_invoice") or user.is_superuser))
        if me and not is_partner:
            obj.fee_earner = me
        if commit:
            obj.save()
        return obj


# Invoice form with dynamic matter filtering

class InvoiceForm(forms.ModelForm):
    matter = forms.ModelChoiceField(
        queryset=Matter.objects.none(),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "id_inv_matter", "required": True})
    )

    class Meta:
        model = Invoice
        fields = ["client", "matter", "notes"]
        widgets = {
            "client": forms.Select(
                attrs={"id": "id_inv_client",
                       "class": "form-select", "required": True}),
            "matter": forms.Select(
                attrs={"id": "id_inv_matter",
                       "class": "form-select", "required": True}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user
        me = getattr(user, "personnel_profile", None)

        # ----- Clients: only those with at least one OPEN matter led by me -----
        if me:
            my_open_matters = Matter.objects.filter(
                closed_at__isnull=True,
                lead_fee_earner=me,
            )
            client_ids = my_open_matters.values_list("client_id", flat=True).distinct()
            clients_qs = Client.objects.filter(id__in=client_ids).order_by("name")

            inst_client_id = getattr(self.instance, "client_id", None)
            if inst_client_id and inst_client_id not in client_ids:
                clients_qs = (
                    Client.objects.filter(
                        id=inst_client_id) | clients_qs).order_by("name")
        else:

            clients_qs = Client.objects.none()

        self.fields["client"].queryset = clients_qs
        self.fields["client"].required = True
        self.fields["matter"].required = True

        # ----- Matters: depends on selected client, and must be led by me & open -----
        cid = None
        data = getattr(self, "data", None)
        if data and data.get("client"):
            try:
                cid = int(data.get("client"))
            except (TypeError, ValueError):
                cid = None
        elif self.instance.pk and self.instance.client_id:
            cid = self.instance.client_id

        if cid and me:
            matters_qs = Matter.objects.filter(
                client_id=cid,
                closed_at__isnull=True,
                lead_fee_earner=me,
            )

            # Include instance matter (e.g.,
            # when re-editing an older invoice) so the form can render
            inst_matter_id = getattr(self.instance, "matter_id", None)
            if inst_matter_id and not matters_qs.filter(pk=inst_matter_id).exists():
                matters_qs = Matter.objects.filter(pk=inst_matter_id) | matters_qs

            self.fields["matter"].queryset = matters_qs.order_by("matter_number")
        else:
            self.fields["matter"].queryset = Matter.objects.none()

    def clean(self):
        cleaned = super().clean()
        client = cleaned.get("client")
        matter = cleaned.get("matter")
        me = getattr(getattr(self, "_user", None), "personnel_profile", None)

        if client and matter and matter.client_id != client.id:
            self.add_error("matter",
                        "Selected matter does not belong to the chosen client.")

        # Enforce: must be led by current user (regardless of partner status)
        if matter and me and matter.lead_fee_earner_id != me.id:
            self.add_error("matter", "You are not the lead fee earner on this matter.")

        return cleaned

# Customized authentication form with Bootstrap styling

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
            "hours_worked": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0"}),
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


