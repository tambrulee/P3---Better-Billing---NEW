from django.db import migrations, models
import django.db.models.deletion

def backfill_client_from_matter(apps, schema_editor):
    WIP = apps.get_model("better_bill_project", "WIP")
    # If you renamed the app label, adjust it above.
    for w in WIP.objects.select_related("matter").only("id", "client_id", "matter_id"):
        if w.client_id is None and w.matter_id:
            # assumes Matter has client FK
            w.client_id = w.matter.client_id
            w.save(update_fields=["client_id"])

def reverse_noop(apps, schema_editor):
    # Nothing to do on reverse
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("better_bill_project", "0015_backfill_wip_client"),  # <- update to your last migration
    ]

    operations = [
        # 1) add as NULLABLE
        migrations.AddField(
            model_name="wip",
            name="client",
            field=models.ForeignKey(
                to="better_bill_project.client",
                on_delete=django.db.models.deletion.PROTECT,
                null=True, blank=True,
            ),
        ),
        # 2) backfill values
        migrations.RunPython(backfill_client_from_matter, reverse_code=reverse_noop),
        # 3) enforce NOT NULL
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
