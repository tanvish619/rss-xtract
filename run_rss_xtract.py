import os
import sys
import time
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

WINDOWS = os.name == "nt"


def run_cmd(command, cwd, title):
    """Open a persistent terminal window running the given command."""
    if WINDOWS:
        return subprocess.Popen(
            ["cmd", "/k", f"title {title} && {command}"],
            cwd=str(cwd),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        return subprocess.Popen(command, cwd=str(cwd), shell=True)


def start_all():
    print("Starting RSS-Xtract...")

    # Start PostgreSQL + Redis
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=str(ROOT),
        check=True,
    )

    # FastAPI
    api = run_cmd(
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        BACKEND,
        "RSS-Xtract FastAPI",
    )

    # Celery
    celery = run_cmd(
        "celery -A app.celery_app worker --loglevel=info --pool=solo",
        BACKEND,
        "RSS-Xtract Celery",
    )

    # Next.js
    frontend = run_cmd(
        "npm run dev",
        FRONTEND,
        "RSS-Xtract Frontend",
    )

    print("\nRSS-Xtract started!")
    print("Frontend : http://localhost:3000")
    print("Backend  : http://localhost:8000")
    print("API Docs : http://localhost:8000/docs")
    print("\nThree terminal windows were opened:")
    print("  1. FastAPI")
    print("  2. Celery")
    print("  3. Next.js")
    print("\nPostgreSQL : localhost:5432")
    print("Redis      : localhost:6379")

    # Store PIDs for optional manual management.
    pid_file = ROOT / ".rss_xtract_pids"
    pid_file.write_text(
        f"{api.pid}\n{celery.pid}\n{frontend.pid}\n",
        encoding="utf-8",
    )


def stop_process_tree(pid):
    if WINDOWS:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except ProcessLookupError:
            pass


def stop_all():
    print("Stopping RSS-Xtract application...")

    pid_file = ROOT / ".rss_xtract_pids"

    if pid_file.exists():
        for line in pid_file.read_text(encoding="utf-8").splitlines():
            if line.strip().isdigit():
                stop_process_tree(int(line.strip()))
        pid_file.unlink(missing_ok=True)

    # Stop only the containers defined by THIS docker-compose.yml.
    subprocess.run(
        ["docker", "compose", "down"],
        cwd=str(ROOT),
        check=False,
    )

    print("\nRSS-Xtract stopped.")
    print("PostgreSQL and Redis containers have been stopped.")
    print("Your Docker volumes/data are preserved.")


def status():
    print("\nDocker containers:")
    subprocess.run(
        ["docker", "compose", "ps"],
        cwd=str(ROOT),
        check=False,
    )

    print("\nExpected local services:")
    print("  Frontend : http://localhost:3000")
    print("  Backend  : http://localhost:8000")
    print("  API Docs : http://localhost:8000/docs")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_rss_xtract.py start")
        print("  python run_rss_xtract.py stop")
        print("  python run_rss_xtract.py restart")
        print("  python run_rss_xtract.py status")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        start_all()
    elif command == "stop":
        stop_all()
    elif command == "restart":
        stop_all()
        time.sleep(2)
        start_all()
    elif command == "status":
        status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
