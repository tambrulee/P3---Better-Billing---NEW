import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from better_bill_project.models import Personnel, TimeEntry, WIP, Invoice, Ledger

DOMAIN = "bestlawfirm.co.uk"

def norm_username_from_name(name: str) -> str:
    slug = re.sub(r"\s+", "_", name.strip())
    slug = re.sub(r"[^A-Za-z0-9_]", "", slug)
    return slug.lower()

class Command(BaseCommand):
    help = "Create User accounts from Personnel + groups/permissions."

    def handle(self, *args, **opts):
        # --- Create groups
        partner, _ = Group.objects.get_or_create(name="Partner")
        fee_earner, _ = Group.objects.get_or_create(name="Fee Earner")

        # --- Ensure custom permission exists
        ct_inv = ContentType.objects.get_for_model(Invoice)
        ct_led = ContentType.objects.get_for_model(Ledger)
        ct_wip = ContentType.objects.get_for_model(WIP)
        ct_te  = ContentType.objects.get_for_model(TimeEntry)

        # Create custom 'post_invoice' perm if missing
        post_perm, _ = Permission.objects.get_or_create(
            codename="post_invoice",
            name="Can post (finalize) invoice",
            content_type=ct_inv,
        )

        # Partner: everything (we’ll assign broad perms)
        partner_perms = Permission.objects.filter(
            content_type__in=[ct_inv, ct_led, ct_wip, ct_te])
        partner.permissions.set(
            partner_perms | Permission.objects.filter(codename="post_invoice"))

        # Fee Earner: can do everything except Post Invoice page (no post_invoice perm)
        fe_codenames = [
            # TimeEntry
            "add_timeentry", "change_timeentry", "view_timeentry",
            # WIP
            "view_wip", "change_wip",
            # Invoice (create & edit)
            "add_invoice", "change_invoice", "view_invoice",
            # Ledger (view)
            "view_ledger",
        ]
        fee_earner.permissions.set(Permission.objects.filter(codename__in=fe_codenames))

        # --- Create users from Personnel
        created = 0
        for p in Personnel.objects.select_related("role"):
            if p.user_id:
                continue
            username = norm_username_from_name(p.name or p.initials or f"user_{p.pk}")
            email = f"{username}@{DOMAIN}"
            user, made = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": p.name.split()[0] if p.name else "",
                    "last_name": " ".join(p.name.split()[1:]) if p.name else ""},
            )
            if made:
                user.set_password("ChangeMe123!")  # temp password
                user.is_active = True
                user.save()
                created += 1

            # Link back to Personnel
            p.user = user
            p.save(update_fields=["user"])

            # Group assignment: Partner if role == "Partner", else Fee Earner
            if p.role and p.role.role.strip().lower() == "partner":
                user.groups.add(partner)
                user.is_staff = True  # access Django admin
                user.is_superuser = True  # optional: full admin
            else:
                user.groups.add(fee_earner)
            user.save()

        self.stdout.write(self.style.SUCCESS(f"Done. Users created: {created}"))
