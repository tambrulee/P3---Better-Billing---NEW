from .models import Personnel

# --- Role aliases (case-insensitive) ---
ROLE_BILLING = {"billing administrator", "billing", "accounts", "finance"}
ROLE_PARTNER = {"partner"}
ROLE_ASSOC_PARTNER = {"associate partner", "assoc partner", "associate_partner"}

class Scope:
    def __init__(self, p):
        self.p = p

    def _role_name(self) -> str:
        # robust against None/whitespace/case
        return (getattr(getattr(self.p, "role", None), "role", "") or "").strip().lower()

    def is_admin(self) -> bool:
        u = getattr(self.p, "user", None)
        return bool(u and u.is_superuser)

    def is_billing(self) -> bool:
        rn = self._role_name()
        return rn in ROLE_BILLING or ("billing" in rn)  # safety net

    def is_partner(self) -> bool:
        return self._role_name() in ROLE_PARTNER

    def is_associate_partner(self) -> bool:
        return self._role_name() in ROLE_ASSOC_PARTNER

    # capabilities (no cashier)
    def can_view_invoice(self) -> bool:
        return any([self.is_admin(), self.is_billing(), self.is_partner(), self.is_associate_partner()])

    def can_create_invoice(self) -> bool:
        return any([self.is_admin(), self.is_partner(), self.is_associate_partner()])

    def can_post_or_delete_invoice(self) -> bool:
        return any([self.is_admin(), self.is_billing()])

    def can_mark_paid(self) -> bool:
        return self.is_admin()  # cashier removed
