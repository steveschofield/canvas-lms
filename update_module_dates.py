import configparser
from datetime import datetime
import requests
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

from canvas_api_utils import build_course_api_url

# Year used when parsing the mm/dd values below.
# Adjust this to the correct academic year before running.
YEAR = 2025

# (label to match, unlock_at mm/dd, lock_at mm/dd)
MODULE_DATE_STRINGS = [
    ("Module 1", "1/12", "1/18"),
    ("Module 2", "1/19", "1/25"),
    ("Module 3", "1/26", "2/1"),
    ("Module 4", "2/2", "2/8"),
    ("Module 5", "2/9", "2/15"),
    ("Module 6", "2/16", "3/1"),
    ("Module 7", "3/2", "3/15"),
    ("Module 8", "3/16", "3/22"),
    ("Module 9", "3/23", "4/5"),
    ("Module 10", "4/6", "4/19"),
    ("Module 11", "4/20", "5/1"),
]

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"


def parse_mmdd(mmdd: str) -> datetime:
    """Convert mm/dd to a datetime using the configured YEAR."""
    return datetime.strptime(f"{YEAR}-{mmdd}", "%Y-%m/%d")


def update_module_dates(course_id, access_token, canvas_domain_url, module_id, unlock_at, lock_at):
    """PUT updated unlock/lock dates for a module."""
    url = build_course_api_url(canvas_domain_url, course_id, f"modules/{module_id}")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "module": {
            "unlock_at": unlock_at.isoformat(),
            "lock_at": lock_at.isoformat() if lock_at else None,
            "published": True,
        }
    }
    # Remove lock_at if not provided to avoid nulling unintentionally
    if payload["module"]["lock_at"] is None:
        payload["module"].pop("lock_at")

    response = requests.put(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if CONFIG_SECTION not in config:
        raise KeyError(f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}")

    course_id = config[CONFIG_SECTION]["COURSE_ID"]
    access_token = config[CONFIG_SECTION]["API_TOKEN"]
    canvas_domain_url = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"]

    canvas = Canvas(canvas_domain_url, access_token)
    try:
        course = canvas.get_course(course_id)
    except CanvasException as exc:
        raise SystemExit(f"Failed to load course {course_id}: {exc}")

    modules = list(course.get_modules())

    for label, unlock_str, lock_str in MODULE_DATE_STRINGS:
        unlock_at = parse_mmdd(unlock_str)
        lock_at = parse_mmdd(lock_str) if lock_str else None

        target = next((m for m in modules if m.name.startswith(label)), None)
        if not target:
            print(f"[skip] No module found starting with '{label}'")
            continue

        try:
            update_module_dates(course_id, access_token, canvas_domain_url, target.id, unlock_at, lock_at)
            print(f"[ok] {target.name}: unlock {unlock_at.date()} lock {lock_at.date() if lock_at else '—'}")
        except requests.HTTPError as exc:
            print(f"[error] {target.name}: {exc.response.status_code} {exc.response.text}")


if __name__ == "__main__":
    main()
