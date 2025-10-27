from __future__ import annotations
from typing import Any
import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TimeEntry, WIP

log = logging.getLogger(__name__)

@receiver(post_save, sender=TimeEntry,
          dispatch_uid="better_bill_timeentry_post_save")
def create_or_sync_wip(sender: type[TimeEntry],
                       instance: TimeEntry,
                       created: bool, **kwargs: Any) -> None:
    """
    Ensure there's a 1:1 WIP row for each TimeEntry.
    - Create on first save.
    - If updating and WIP exists & is UNBILLED, sync selected fields.
    - If updating and WIP missing (legacy rows), create it.
    """
    def _sync() -> None:
        try:
            if created:
                obj, made = WIP.objects.get_or_create(
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
                log.info(
                    "WIP %s for TE id=%s (created=%s)",
                    getattr(obj, "id", None),
                    instance.id, made)
                return

            # Updates
            try:
                wip = instance.wip
            except WIP.DoesNotExist:
                wip = WIP.objects.create(
                    time_entry=instance,
                    client=instance.client,
                    matter=instance.matter,
                    fee_earner=instance.fee_earner,
                    activity_code=instance.activity_code,
                    hours_worked=instance.hours_worked,
                    narrative=instance.narrative,
                    status="unbilled",
                )
                log.info("WIP created for legacy TE id=%s -> WIP id=%s",
                         instance.id, wip.id)
                return

            # Don’t mutate billed/written-off items
            if wip.status != "unbilled":
                log.info("Skip WIP sync for TE id=%s (status=%s)",
                         instance.id, wip.status)
                return

            changed_fields: list[str] = []
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
                    changed_fields.append(field)

            if changed_fields:
                wip.save(update_fields=changed_fields + ["updated_at"])
                log.info("WIP id=%s synced fields=%s for TE id=%s",
                         wip.id, ", ".join(changed_fields), instance.id)
        except Exception:
            log.exception(
                "create_or_sync_wip failed for TE id=%s",
                getattr(instance, "id", None))

    # Run after the transaction commits (safe with views that use atomic blocks)
    transaction.on_commit(_sync)
