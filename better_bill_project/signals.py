from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TimeEntry, WIP

@receiver(post_save, sender=TimeEntry)
def create_or_sync_wip(sender, instance: TimeEntry, created, **kwargs):
    def _sync():
        if created:
            # Idempotent create
            WIP.objects.get_or_create(
                time_entry=instance,
                defaults={
                    "client": instance.client,
                    "matter": instance.matter,
                    "fee_earner": instance.fee_earner,
                    "activity_code": instance.activity_code,
                    "hours_worked": instance.hours_worked,
                    "narrative": instance.narrative,
                    "status": "unbilled",
                },
            )
        else:
            try:
                wip = instance.wip
            except WIP.DoesNotExist:
                WIP.objects.create(
                    time_entry=instance,
                    client=instance.client,
                    matter=instance.matter,
                    fee_earner=instance.fee_earner,
                    activity_code=instance.activity_code,
                    hours_worked=instance.hours_worked,
                    narrative=instance.narrative,
                    status="unbilled",
                )
            else:
                changed = False
                for field, value in {
                    "client": instance.client,
                    "matter": instance.matter,
                    "fee_earner": instance.fee_earner,
                    "activity_code": instance.activity_code,
                    "hours_worked": instance.hours_worked,
                    "narrative": instance.narrative,
                }.items():
                    if getattr(wip, field) != value:
                        setattr(wip, field, value)
                        changed = True
                if changed:
                    wip.save()

    # Run after transaction commits
    transaction.on_commit(_sync)