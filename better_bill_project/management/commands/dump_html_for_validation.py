from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.conf import settings
from pathlib import Path

# ---- Your named URLs (from your urls.py) ----
URL_NAMES = [
    "index",
    "create-invoice",
    "record-time",
    "view-invoice",
    "post-invoice",
]

# You can also fetch literal paths (no reverse needed)
LITERAL_PATHS = [
    "/accounts/login/",
    "/accounts/password_reset/",
]

def safe_reverse(name, **kwargs):
    try:
        return reverse(name, kwargs=kwargs or None)
    except NoReverseMatch:
        return None

class Command(BaseCommand):
    help = "Render key pages and save HTML files for HTML5 validation."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="tmp/validation_html")
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **opts):
        # --- DEV-ONLY: ensure common hosts are allowed (fixes 400 DisallowedHost) ---
        if "testserver" not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [
                "testserver", "127.0.0.1", "localhost"
            ]

        out_dir = Path(opts["out"])
        out_dir.mkdir(parents=True, exist_ok=True)

        User = get_user_model()
        if not User.objects.filter(username=opts["username"]).exists():
            self.stderr.write(self.style.ERROR("User not found."))
            return

        client = Client()
        if not client.login(username=opts["username"], password=opts["password"]):
            self.stderr.write(self.style.ERROR("Login failed. Check credentials."))
            return

        # Build targets (mix of reverse()d names and literal paths)
        targets = []
        for name in URL_NAMES:
            path = safe_reverse(name)
            if path:
                targets.append((name, path))
            else:
                self.stderr.write(
                    self.style.WARNING(f"Skipping {name}: NoReverseMatch"))

        for path in LITERAL_PATHS:
            slug = path.strip("/").replace("/", "_") or "root"
            targets.append((slug, path))

        # --- Fetch and write files (skip non-document/fragment responses) ---
        for slug, path in targets:
            # Make the request with an explicit host to avoid DisallowedHost (400)
            resp = client.get(path, follow=True, HTTP_HOST="127.0.0.1")

            # Fragment / non-HTML filter
            content_type = resp.headers.get("Content-Type", "")
            body = resp.content
            is_html = ("text/html" in content_type) or (content_type == "")
            has_doctype = b"<!DOCTYPE HTML" in body[:512].upper()

            if not (is_html and has_doctype):
                self.stderr.write(self.style.WARNING(
                    f"Skipping {slug}: not a full HTML document"
                ))
                continue

            # Save valid full documents
            outfile = out_dir / f"{slug}.html"
            outfile.write_bytes(body)
            self.stdout.write(self.style.SUCCESS(
                f"{slug}: {resp.status_code} -> {outfile}"))

