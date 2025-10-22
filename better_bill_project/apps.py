from django.apps import AppConfig

class BetterBillProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "better_bill_project"

    def ready(self):
        from . import signals  # noqa: F401  <- important # pyright: ignore[reportUnusedImport]
