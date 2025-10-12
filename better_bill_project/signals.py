from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TimeEntry, WIP

@receiver(post_save, sender=TimeEntry)
def create_wip_from_timeentry(sender, instance, created, **kwargs):
    if not created:
        # Optionally keep WIP in sync if a time entry is edited
        if hasattr(instance, "wip"):
            wip = instance.wip
            wip.matter = instance.matter
            wip.fee_earner = instance.fee_earner
            wip.activity_code = instance.activity_code
            wip.hours_worked = instance.hours_worked
            wip.narrative = instance.narrative
            wip.save(update_fields=["matter","fee_earner","activity_code","hours_worked","narrative","updated_at"])
        return

    # On first creation, make a WIP row
    WIP.objects.get_or_create(
        time_entry=instance,
        defaults={
            "matter": instance.matter,
            "fee_earner": instance.fee_earner,
            "activity_code": instance.activity_code,
            "hours_worked": instance.hours_worked,
            "narrative": instance.narrative,
            "status": "unbilled",
        },
    )
