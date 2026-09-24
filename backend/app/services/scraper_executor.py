import json
import subprocess
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.feed_version import FeedVersion


def execute_scraper(
    db: Session,
    feed_version_id: str
):
    version = (
        db.query(FeedVersion)
        .filter(
            FeedVersion.id == feed_version_id
        )
        .first()
    )

    if version is None:
        raise ValueError("Feed version not found")

    if not version.script_path:
        raise ValueError("Scraper path not found")

    scraper_path = Path(version.script_path)

    if not scraper_path.exists():
        raise FileNotFoundError(
            f"Scraper file not found: {scraper_path}"
        )

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(scraper_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Scraper execution timed out after 60 seconds"
        )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = "Scraper execution failed"

        raise RuntimeError(error_message)

    output = result.stdout.strip()

    if not output:
        return []

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        start_idx = output.find("[")
        end_idx = output.rfind("]")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(output[start_idx : end_idx + 1])
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Scraper returned invalid JSON: {e}")
        raise RuntimeError(f"Scraper returned invalid JSON output: {output[:200]}")