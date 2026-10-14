"""Build a source-only archive without credentials or runtime data."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "barber-booking-source.zip"
ROOT_FILES = (".editorconfig", ".gitignore", ".dockerignore", "README.md", "compose.yaml", "Dockerfile", "render.yaml")
SOURCE_DIRS = (".github", "backend", "frontend", "docs", "scripts")
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "coverage", "htmlcov", "dist", "build", "staticfiles", "media", ".local", ".tools", ".vscode", ".idea", "test-results"}
EXCLUDED_FILES = {".DS_Store", "Thumbs.db", "Desktop.ini"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".zip", ".sqlite3", ".tsbuildinfo", ".swp", ".swo"}


def allowed(path):
    relative = path.relative_to(ROOT)
    if path.is_symlink() or any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in EXCLUDED_FILES or path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
        return False
    return not path.name.startswith(".coverage") and not path.name.endswith("~")


def source_files(directory):
    for path in sorted(directory.iterdir()):
        if not allowed(path):
            continue
        if path.is_dir():
            yield from source_files(path)
        elif path.is_file():
            yield path


def main():
    files = [ROOT / name for name in ROOT_FILES]
    for name in SOURCE_DIRS:
        files.extend(source_files(ROOT / name))
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, "barber-booking/" + path.relative_to(ROOT).as_posix())
    with ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Source archive integrity check failed.")
    print(f"Created {OUTPUT.name}: {len(files)} source files, {OUTPUT.stat().st_size:,} bytes.")


if __name__ == "__main__":
    main()
