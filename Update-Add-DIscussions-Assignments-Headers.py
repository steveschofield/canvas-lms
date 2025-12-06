import configparser
import requests
from typing import Optional, List, Dict

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
API_TOKEN = config[CONFIG_SECTION]['API_TOKEN'].strip()
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]['CANVAS_DOMAIN_URL'].rstrip('/')

# If CANVAS_DOMAIN_URL already includes "https://", this is fine.
# Example: https://mcc.instructure.com -> https://mcc.instructure.com/api/v1
CANVAS_BASE_URL = f"{CANVAS_DOMAIN_URL}/api/v1"


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }


def find_module_by_name_contains(course_id: int, keyword: str) -> Optional[Dict]:
    """
    Return the first module whose name *contains* the keyword (case-insensitive).
    Example: keyword="Module 2" matches "Module 2 – Week Two".
    """
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/modules"
    params = {"per_page": 100}

    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()

    keyword = keyword.lower()
    for module in resp.json():
        name = (module.get("name") or "").lower()
        if keyword in name:
            return module

    return None


def get_module_items(course_id: int, module_id: int) -> List[Dict]:
    """
    Return all items in a module.
    """
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/modules/{module_id}/items"
    params = {"per_page": 100}
    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def header_exists_in_module(items: List[Dict], title: str) -> bool:
    """
    Check if a Text Header (SubHeader) with the given title already exists.
    """
    for item in items:
        if item.get("type") == "SubHeader" and (item.get("title") or "") == title:
            return True
    return False


def create_subheader_item(
    course_id: int,
    module_id: int,
    title: str,
    position: int,
) -> Dict:
    """
    Create a Text Header (SubHeader) in the given module at a specific position.
    """
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/modules/{module_id}/items"
    data = {
        "module_item[title]": title,
        "module_item[type]": "SubHeader",   # Canvas type for "Text Header"
        "module_item[position]": position,
        "module_item[indent]": 0,
        "module_item[published]": True,
    }

    resp = requests.post(url, headers=get_headers(), data=data)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    for n in range(2, 11):  # Modules 2–10 inclusive
        print("=" * 60)
        module_keyword = f"Module {n}"
        print(f"Processing module containing: {module_keyword!r} ...")

        # 1) Find module by name containing "Module n"
        module = find_module_by_name_contains(COURSE_ID, module_keyword)
        if not module:
            print(f"  ERROR: No module name contains '{module_keyword}'. Skipping.")
            continue

        module_id = module["id"]
        module_name_full = module.get("name")
        print(f"  Found module: {module_name_full!r} (ID={module_id})")

        # 2) Get current items to check for existing headers
        items = get_module_items(COURSE_ID, module_id)

        # 3) Ensure "Discussions" header at position 1
        discussions_title = "Discussions"
        if header_exists_in_module(items, discussions_title):
            print(f"  Header {discussions_title!r} already exists; skipping.")
        else:
            print(f"  Creating header {discussions_title!r} at position 1...")
            created_disc = create_subheader_item(
                COURSE_ID,
                module_id,
                title=discussions_title,
                position=1,
            )
            print(f"    Created (item id={created_disc.get('id')}, position={created_disc.get('position')})")

        # 4) Refresh items (optional but safer if you care about positions)
        items = get_module_items(COURSE_ID, module_id)

        # 5) Ensure "Assignments" header at position 3
        assignments_title = "Assignments"
        if header_exists_in_module(items, assignments_title):
            print(f"  Header {assignments_title!r} already exists; skipping.")
        else:
            print(f"  Creating header {assignments_title!r} at position 3...")
            created_assign = create_subheader_item(
                COURSE_ID,
                module_id,
                title=assignments_title,
                position=3,
            )
            print(f"    Created (item id={created_assign.get('id')}, position={created_assign.get('position')})")

        print("  Done with this module.")

    print("=" * 60)
    print("Completed processing modules 2–10.")


if __name__ == "__main__":
    main()