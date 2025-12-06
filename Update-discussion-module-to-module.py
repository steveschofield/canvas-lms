import configparser
import requests
from typing import Optional, List

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

CANVAS_BASE_URL = f"{CANVAS_DOMAIN_URL}/api/v1"


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }


def find_module_by_name_contains(course_id: int, keyword: str) -> Optional[dict]:
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


def find_discussion_by_title_contains(course_id: int, keyword: str) -> Optional[dict]:
    """
    Return the first discussion whose title *contains* the keyword (case-insensitive).
    Example: keyword="Module 2" matches "Module 2 Discussion Board".
    """
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/discussion_topics"
    params = {"per_page": 100}

    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()

    keyword = keyword.lower()
    for topic in resp.json():
        title = (topic.get("title") or "").lower()
        if keyword in title:
            return topic

    return None


def get_module_items(course_id: int, module_id: int) -> List[dict]:
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/modules/{module_id}/items"
    params = {"per_page": 100}
    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def discussion_already_in_module(course_id: int, module_id: int, discussion_id: int) -> bool:
    items = get_module_items(course_id, module_id)
    for item in items:
        if item.get("type") == "Discussion" and item.get("content_id") == discussion_id:
            return True
    return False


def add_discussion_to_module(course_id: int, module_id: int, discussion_id: int, item_title: str) -> dict:
    url = f"{CANVAS_BASE_URL}/courses/{course_id}/modules/{module_id}/items"

    data = {
        "module_item[type]": "Discussion",
        "module_item[content_id]": discussion_id,
        "module_item[title]": item_title,
    }

    resp = requests.post(url, headers=get_headers(), data=data)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    for n in range(2, 11):  # Modules 2–10
        print("=" * 60)
        print(f"Processing MODULE {n}...")

        module_keyword = f"Module {n}"
        discussion_keyword = f"Module {n}"

        # 1) Find a module where the name contains "Module n"
        module = find_module_by_name_contains(COURSE_ID, module_keyword)
        if not module:
            print(f"  ERROR: No module name contains '{module_keyword}'. Skipping.")
            continue

        module_id = module["id"]
        module_name_full = module["name"]
        print(f"  Found module: {module_name_full!r} (ID={module_id})")

        # 2) Find a discussion whose title contains "Module n"
        discussion = find_discussion_by_title_contains(COURSE_ID, discussion_keyword)
        if not discussion:
            print(f"  ERROR: No discussion title contains '{discussion_keyword}'. Skipping.")
            continue

        discussion_id = discussion["id"]
        discussion_title_full = discussion["title"]
        print(f"  Found discussion: {discussion_title_full!r} (ID={discussion_id})")

        # 3) Skip if already added
        if discussion_already_in_module(COURSE_ID, module_id, discussion_id):
            print("  Discussion already in module; skipping.")
            continue

        # 4) Build label shown inside module
        shown_as = f"Discuss {module_name_full}"

        # 5) Add discussion
        print(f"  Adding discussion as: {shown_as!r} ...")
        added = add_discussion_to_module(
            COURSE_ID, module_id, discussion_id, shown_as
        )

        print("  ✔ Added successfully")
        print(f"    Module Item ID: {added.get('id')}")
        print(f"    Position:       {added.get('position')}")


if __name__ == "__main__":
    main()