# better_bill_project/migrations/00xx_sync_wip_client.py
from django.db import migrations, models
import django.db.models.deletion

def backfill_client_from_matter(apps, schema_editor):
    WIP = apps.get_model("better_bill_project", "WIP")
    for w in WIP.objects.only("id", "client_id", "matter_id").select_related("matter"):
        if w.client_id is None and w.matter_id:
            w.client_id = w.matter.client_id
            w.save(update_fields=["client_id"])

class Migration(migrations.Migration):
    dependencies = [
        ("better_bill_project", "0016_wip_client_backfill"),
    ]

    operations = [
        # 1) Tell Django the field exists (state change only; no DB op)
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="wip",
                    name="client",
                    field=models.ForeignKey(
                        to="better_bill_project.client",
                        on_delete=django.db.models.deletion.PROTECT,
                        null=True, blank=True,
                    ),
                ),
            ],
        ),
        # 2) Backfill any NULLs using matter.client
        migrations.RunPython(backfill_client_from_matter, migrations.RunPython.noop),
        # 3) Now enforce NOT NULL and the FK constraint in the DB
        migrations.AlterField(
            model_name="wip",
            name="client",
            field=models.ForeignKey(
                to="better_bill_project.client",
                on_delete=django.db.models.deletion.PROTECT,
                null=False, blank=False,
            ),
        ),
    ]
