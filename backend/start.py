import os
import subprocess
import sys


def run(*command):
    subprocess.run(command, check=True)


def main():
    run(sys.executable, "manage.py", "migrate", "--noinput")

    seed_demo = os.environ.get("SEED_DEMO_DATA", "False").strip().lower()
    if seed_demo not in {"true", "false"}:
        raise SystemExit("SEED_DEMO_DATA must be True or False.")
    if seed_demo == "true":
        run(sys.executable, "manage.py", "seed_demo")

    os.execvp(
        "gunicorn",
        ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"],
    )


if __name__ == "__main__":
    main()
