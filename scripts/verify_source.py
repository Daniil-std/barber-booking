"""Redacted checks of publishable source, Git history and the source ZIP."""
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = {".env", ".git", ".local", ".tools", "node_modules", ".venv", "venv", "dist", "staticfiles", "__pycache__", "postgres-data"}
SENSITIVE_PATTERNS = [rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", rb"ghp_[A-Za-z0-9]{30,}", rb"AKIA[A-Z0-9]{16}"]


def main():
    # Read credentials only for exact-match comparison; never print them.
    private_values = []
    env_path = ROOT / "backend" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            key, sep, value = line.partition("=")
            if sep and key in {"DJANGO_SECRET_KEY", "POSTGRES_PASSWORD", "DATABASE_URL"}:
                value = value.strip().strip("\"'")
                if len(value) >= 12:
                    private_values.append(value.encode())

    def inspect(name, data):
        parts = Path(name).parts
        if any(part in FORBIDDEN for part in parts) or (Path(name).name.startswith(".env.") and not name.endswith(".env.example")) or name.endswith(".zip"):
            raise RuntimeError(f"Private/generated path in source: {name}")
        if any(value in data for value in private_values) or any(re.search(pattern, data) for pattern in SENSITIVE_PATTERNS):
            raise RuntimeError(f"Potential secret in {name}; contents redacted")

    files = subprocess.check_output(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    count = 0
    for name in sorted(set(files) - {""}):
        inspect(name, (ROOT / name).read_bytes())
        count += 1
    history = subprocess.check_output(["git", "log", "--all", "-p", "--format="], cwd=ROOT)
    if any(value in history for value in private_values) or any(re.search(pattern, history) for pattern in SENSITIVE_PATTERNS):
        raise RuntimeError("Potential secret in Git history; contents redacted")
    with ZipFile(ROOT / "barber-booking-source.zip") as archive:
        for entry in archive.infolist():
            inspect(entry.filename, archive.read(entry))
        for required in ("Dockerfile", "render.yaml", ".github/workflows/ci.yml"):
            assert "barber-booking/" + required in archive.namelist(), required
        assert archive.testzip() is None
        print(f"PASS: {count} publishable files, Git history, {len(archive.infolist())} ZIP entries; no matched secrets or forbidden paths")
    print("This exact-value/pattern scan is not a comprehensive credential scanner.")


if __name__ == "__main__":
    main()
