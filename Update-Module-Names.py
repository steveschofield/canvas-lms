import configparser
import requests
from typing import Optional, Dict, List, Tuple

# --------------------------------------------------
# Load configuration
# --------------------------------------------------
CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

if CONFIG_SECTION not in config:
    raise KeyError(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

COURSE_ID = int(config[CONFIG_SECTION]["COURSE_ID"])
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"]


# --------------------------------------------------
# Desired module titles for 1–10
# --------------------------------------------------
NEW_TITLES: Dict[int, str] = {
    1: "Module 1 - 1.0 Penetration Testing: Before You Begin",
    2: "Module 2 - 2.0 Applying Pre-Engagement Activities",
    3: "Module 3 - 3.0 Enumeration and Reconnaissance",
    4: "Module 4 - 4.0 Scanning and Identifying Vulnerabilities",
    5: "Module 5 - 5.0 Conducting Pentest Attacks",
    6: "Module 6 - 6.0 Web-based Attacks",
    7: "Module 7 - 7.0 Enterprise Attacks",
    8: "Module 8 - 8.0 Specialized Attacks",
    9: "Module 9 - 9.0 Performing Penetration Testing Tasks",
    10: "Module 10 - 10.0 Reporting and Recommendations",
}

MODULE_NUMBERS: List[int] = list(NEW_TITLES.keys())


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }


def get_all_modules(course_id: int) -> list:
    """
    Retrieve all modules (up to 100) for this course.
    If you have more than 100, we can add pagination.
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/modules"
    params = {"per_page": 100}

    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def find_module_by_number_prefix(course_id: int, module_number: int) -> Optional[dict]:
    """
    Find the first module whose name starts with 'Module {module_number}'.

    Example match:
      'Module 1 - 1.0 Penetration Testing: Before You Begin'
      'Module 1' (plain)
    """
    prefix = f"Module {module_number}"
    modules = get_all_modules(course_id)

    for module in modules:
        name = module.get("name", "")
        if name.startswith(prefix):
            return module

    return None


def update_module_name(course_id: int, module_id: int, new_name: str) -> dict:
    """
    Update the module's name.

    PUT /api/v1/courses/:course_id/modules/:id
    with module[name]
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/modules/{module_id}"
    data = {"module[name]": new_name}

    resp = requests.put(url, headers=get_headers(), data=data)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    print(f"Renaming modules 1–10 in course {COURSE_ID}...\n")

    successes: List[Tuple[str, str]] = []
    failures: List[Tuple[str, str]] = []

    for number in MODULE_NUMBERS:
        new_title = NEW_TITLES[number]
        prefix = f"Module {number}"

        print(f"--- Processing modules starting with {prefix!r} ---")
        print(f"  New desired title: {new_title!r}")

        try:
            module = find_module_by_number_prefix(COURSE_ID, number)
            if not module:
                msg = f"No module found whose name starts with {prefix!r}."
                print("  ERROR:", msg)
                failures.append((prefix, msg))
                print()
                continue

            old_name = module.get("name", f"(id {module.get('id')})")
            module_id = module["id"]
            print(f"  Found module: {old_name!r} (ID: {module_id})")
            print(f"  Renaming to: {new_title!r}")

            updated = update_module_name(COURSE_ID, module_id, new_title)

            print(f"  ✔ Updated. Canvas now shows: {updated.get('name')!r}")
            successes.append((old_name, updated.get("name", "")))

        except Exception as e:
            msg = f"Exception: {e}"
            print("  ERROR:", msg)
            failures.append((prefix, msg))

        print()  # blank line between modules

    # Summary
    print("====================================================")
    print("Summary:")
    print(f"  Successful renames: {len(successes)}")
    for old, new in successes:
        print(f"    - {old!r}  ->  {new!r}")

    if failures:
        print(f"\n  Failures: {len(failures)}")
        for prefix, err in failures:
            print(f"    - Prefix {prefix!r}: {err}")


if __name__ == "__main__":
    main()