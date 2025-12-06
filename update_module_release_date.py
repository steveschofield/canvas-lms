import configparser
import requests
from datetime import datetime, timezone, timedelta


# --------------------------------------------------
# Load configuration
# --------------------------------------------------
CONFIG_PATH = 'etc/config.txt'
CONFIG_SECTION = 'canvas-lms-test'

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

if CONFIG_SECTION not in config:
    raise KeyError(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

COURSE_ID = int(config[CONFIG_SECTION]['COURSE_ID'])
API_TOKEN = config[CONFIG_SECTION]['API_TOKEN']
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]['CANVAS_DOMAIN_URL']
SEMESTER_YEAR = int(config[CONFIG_SECTION].get('SEMESTER_YEAR', 2026))


# --------------------------------------------------
# Module schedule (name -> mm/dd)
# --------------------------------------------------
MODULE_SCHEDULE = {
    "Module 1": "1/12",
    "Module 2": "1/19",
    "Module 3": "1/26",
    "Module 4": "2/2",
    "Module 5": "2/9",
    "Module 6": "2/16",
    "Module 7": "3/2",
    "Module 8": "3/16",
    "Module 9": "3/23",
    "Module 10": "4/6",
    "Module 11": "4/20",
}

# Time of day for release (GMT-5)
RELEASE_HOUR = 0
RELEASE_MINUTE = 0


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def parse_mmdd_to_iso(mmdd: str, year: int) -> str:
    """
    Convert '1/12' to an ISO8601 timestamp with GMT-5 offset.
    Example: '2026-01-12T00:00:00-05:00'
    """
    month, day = map(int, mmdd.split("/"))

    # Naive datetime for the given date & time
    dt = datetime(year, month, day, RELEASE_HOUR, RELEASE_MINUTE, 0)

    # Apply fixed GMT-5 offset
    eastern_offset = timedelta(hours=-5)
    dt = dt.replace(tzinfo=timezone(eastern_offset))

    return dt.isoformat()


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }


def find_module_by_name(course_id: int, module_name: str):
    """
    Return module object by its name, or None if not found.
    Assumes < 100 modules in course (adjust per_page if needed).
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/modules"
    params = {"per_page": 100}

    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()

    for module in resp.json():
        if module.get("name") == module_name:
            return module

    return None


def update_module_unlock_date(course_id: int, module_id: int, unlock_at_iso: str):
    """
    PUT update on module[unlock_at].
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/modules/{module_id}"
    data = {"module[unlock_at]": unlock_at_iso}

    resp = requests.put(url, headers=get_headers(), data=data)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    print(f"Updating module release dates for course {COURSE_ID}...\n")

    successes = []
    failures = []

    for module_name, date_str in MODULE_SCHEDULE.items():
        try:
            print(f"--- Processing {module_name!r} (date {date_str}) ---")

            module = find_module_by_name(COURSE_ID, module_name)
            if not module:
                msg = f"Module {module_name!r} not found in course {COURSE_ID}."
                print("  ERROR:", msg)
                failures.append((module_name, msg))
                continue

            module_id = module["id"]
            unlock_at_iso = parse_mmdd_to_iso(date_str, SEMESTER_YEAR)
            print(f"  Found ID: {module_id}")
            print(f"  Setting unlock_at to: {unlock_at_iso}")

            updated = update_module_unlock_date(COURSE_ID, module_id, unlock_at_iso)

            print(f"  ✔ Updated. Canvas unlock_at: {updated.get('unlock_at')}")
            successes.append((module_name, unlock_at_iso))

        except Exception as e:
            msg = f"Exception while updating {module_name!r}: {e}"
            print("  ERROR:", msg)
            failures.append((module_name, msg))

        print()  # blank line between modules

    # Summary
    print("====================================================")
    print("Update summary:")
    print(f"  Successful updates: {len(successes)}")
    for name, ts in successes:
        print(f"    - {name}: {ts}")

    if failures:
        print(f"\n  Failures: {len(failures)}")
        for name, err in failures:
            print(f"    - {name}: {err}")


if __name__ == "__main__":
    main()