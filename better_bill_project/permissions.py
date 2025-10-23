class Scope:
    def __init__(self, p: Personnel):
        self.p = p

    def _ids_self_and_delegates(self):
        if self.p.is_admin:
            return []
        ids = [self.p.user_id] if self.p.user_id else []
        if self.p.is_partner or self.p.is_associate_partner:
            ids += list(self.p.delegate_user_ids())
        return ids

    # capability checks (unchanged in meaning)
    def can_view_invoice(self) -> bool:
        return any([
            self.p.is_admin, self.p.is_billing, self.p.is_cashier,
            self.p.is_partner, self.p.is_associate_partner
        ])

    def can_create_invoice(self) -> bool:
        return any([self.p.is_admin, self.p.is_partner, self.p.is_associate_partner])

    def can_post_or_delete_invoice(self) -> bool:
        return any([self.p.is_admin, self.p.is_billing])

    def can_mark_paid(self) -> bool:
        return any([self.p.is_admin, self.p.is_cashier])
