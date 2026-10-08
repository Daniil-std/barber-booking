"""Create ignored local credentials without printing passwords or overwriting files."""
import argparse
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("--portable", action="store_true", help="Use the workspace PostgreSQL server on port 5433.")
args = parser.parse_args()
target = ROOT / "backend" / ".env"
if target.exists():
    print("backend/.env already exists; no changes made.")
else:
    password = secrets.token_urlsafe(32)
    target.write_text(
        f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n"
        "DJANGO_DEBUG=True\nDJANGO_ALLOWED_HOSTS=127.0.0.1,localhost\n"
        "DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173\n"
        "POSTGRES_DB=form_studio\nPOSTGRES_USER=form_studio\n"
        f"POSTGRES_PASSWORD={password}\nPOSTGRES_HOST=127.0.0.1\n"
        f"POSTGRES_PORT={5433 if args.portable else 5432}\n",
        encoding="utf-8",
    )
    if args.portable:
        local = ROOT / ".local"
        local.mkdir(exist_ok=True)
        (local / "pg-password").write_text(password, encoding="utf-8")
    print("Created ignored local environment files. Credentials were not printed.")
