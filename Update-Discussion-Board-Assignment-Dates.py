#!/usr/bin/env python3
"""
Update Canvas discussion boards for Module 1–10 using the same date schedule
you're using for assignments.

Logic:
- Find discussion topics whose titles contain 'Module X'
- Use X as the module/chapter number
- Look up dates in DATES[module]
- Update:
    discussion_topic[delayed_post_at] = Available From
    discussion_topic[lock_at]         = Due Date (Available Until)
- If the discussion has an assignment_id (graded discussion), also update:
    assignment[unlock_at]             = Available From
    assignment[due_at]                = Due Date
    assignment[lock_at]               = Due Date
"""

import configparser
import requests
import re
from datetime import datetime

# --------------------------------------------------------------------
# Config
# --------------------------------------------------------------------

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

YEAR = 2026               # adjust for the term year
TZ_OFFSET = "-05:00"      # America/Detroit in standard time
AVAILABLE_TIME = "00:00:00"
DUE_TIME = "23:59:00"

DRY_RUN = False            # set to False to actually update Canvas

# Per-module dates (same as you provided)
# Format: "M/D"
DATES = {
    1: {"available": "1/12", "due": "1/18"},  # Module 1
    2: {"available": "1/19", "due": "1/25"},  # Module 2
    3: {"available": "1/26", "due": "2/1"},   # Module 3
    4: {"available": "2/2",  "due": "2/8"},   # Module 4
    5: {"available": "2/9",  "due": "2/15"},  # Module 5
    6: {"available": "2/16", "due": "3/1"},   # Module 6
    7: {"available": "3/2",  "due": "3/15"},  # Module 7
    8: {"available": "3/16", "due": "3/22"},  # Module 8
    9: {"available": "3/23", "due": "4/5"},   # Module 9
    10: {"available": "4/6", "due": "4/19"},  # Module 10
}

# --------------------------------------------------------------------
# Load Canvas config
# --------------------------------------------------------------------

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

if CONFIG_SECTION not in config:
    raise KeyError(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

COURSE_ID = int(config[CONFIG_SECTION]["COURSE_ID"])
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"].rstrip("/")


# --------------------------------------------------------------------
# Canvas helpers
# --------------------------------------------------------------------

def canvas_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }


def list_discussions(course_id: int):
    """
    List all discussion topics for a course (handles pagination).
    """
    topics = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/discussion_topics"
    params = {"per_page": 100}

    while url:
        r = requests.get(url, headers=canvas_headers(), params=params)
        r.raise_for_status()
        topics.extend(r.json())

        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                start = part.find("<") + 1
                end = part.find(">")
                next_url = part[start:end]
                break

        url = next_url
        params = {}

    return topics


def update_discussion_dates(course_id: int, topic_id: int,
                            delayed_post_at_iso: str, lock_at_iso: str):
    """
    Update delayed_post_at (Available From) and lock_at (Available Until)
    for a discussion topic.
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/discussion_topics/{topic_id}"
    payload = {
        "discussion_topic[delayed_post_at]": delayed_post_at_iso,
        "discussion_topic[lock_at]": lock_at_iso,
    }
    r = requests.put(url, headers=canvas_headers(), data=payload)
    r.raise_for_status()
    return r.json()


def list_assignments(course_id: int):
    """
    List all assignments for a course (used for graded discussions with assignment_id).
    """
    assignments = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/assignments"
    params = {"per_page": 100}

    while url:
        r = requests.get(url, headers=canvas_headers(), params=params)
        r.raise_for_status()
        assignments.extend(r.json())

        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                start = part.find("<") + 1
                end = part.find(">")
                next_url = part[start:end]
                break

        url = next_url
        params = {}

    return assignments


def update_assignment_dates(course_id: int, assignment_id: int,
                            unlock_at_iso: str, due_at_iso: str):
    """
    Update unlock_at, due_at, and lock_at for an assignment (e.g., graded discussion).
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    payload = {
        "assignment[unlock_at]": unlock_at_iso,
        "assignment[due_at]": due_at_iso,
        "assignment[lock_at]": due_at_iso,  # Available Until = Due Date
    }
    r = requests.put(url, headers=canvas_headers(), data=payload)
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def build_iso(date_str: str, time_str: str) -> str:
    """
    Convert 'M/D' + time to 'YYYY-MM-DDTHH:MM:SS-05:00'
    """
    month, day = map(int, date_str.split("/"))
    _ = datetime(YEAR, month, day)  # validate the date
    return f"{YEAR:04d}-{month:02d}-{day:02d}T{time_str}{TZ_OFFSET}"


def extract_module_from_title(title: str):
    """
    Extract module/chapter number from titles like:
      'Module 1 Discussion Board'
      'Module 10 - Something'
    Returns int or None.
    """
    m = re.search(r"Module\s+(\d+)", title, re.IGNORECASE)
    if not m:
        return None
    return int(m.group(1))


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    print(f"Course ID: {COURSE_ID}")
    print(f"DRY_RUN = {DRY_RUN}\n")

    topics = list_discussions(COURSE_ID)
    assignments = {a["id"]: a for a in list_assignments(COURSE_ID)}

    for topic in topics:
        title = topic.get("title", "")
        topic_id = topic.get("id")

        module_num = extract_module_from_title(title)
        if module_num is None:
            print(f"[SKIP] '{title}' → no 'Module X' pattern found.")
            continue

        if module_num not in DATES:
            print(f"[SKIP] '{title}' → Module {module_num} not in DATES table.")
            continue

        date_info = DATES[module_num]
        available_str = date_info["available"]
        due_str = date_info["due"]

        delayed_post_at_iso = build_iso(available_str, AVAILABLE_TIME)
        lock_at_iso = build_iso(due_str, DUE_TIME)

        print(f"[MATCH] Discussion '{title}' → Module {module_num}")
        print(f"        Available From (delayed_post_at): {delayed_post_at_iso}")
        print(f"        Available Until (lock_at):        {lock_at_iso}")

        assignment_id = topic.get("assignment_id")

        if assignment_id:
            print(f"        Has graded assignment_id: {assignment_id}")
            unlock_at_iso = delayed_post_at_iso
            due_at_iso = lock_at_iso
            print(f"        Assignment unlock_at: {unlock_at_iso}")
            print(f"        Assignment due_at / lock_at: {due_at_iso}")

        if DRY_RUN:
            print("        (DRY RUN: no changes applied)\n")
            continue

        # Update discussion dates
        updated_topic = update_discussion_dates(COURSE_ID, topic_id,
                                                delayed_post_at_iso, lock_at_iso)
        print(f"        [UPDATED] Discussion delayed_post_at: {updated_topic.get('delayed_post_at')}")
        print(f"        [UPDATED] Discussion lock_at:        {updated_topic.get('lock_at')}")

        # If graded discussion, also update its assignment
        if assignment_id and assignment_id in assignments:
            updated_assignment = update_assignment_dates(
                COURSE_ID,
                assignment_id,
                unlock_at_iso,
                due_at_iso,
            )
            print(f"        [UPDATED] Assignment unlock_at: {updated_assignment.get('unlock_at')}")
            print(f"        [UPDATED] Assignment due_at:    {updated_assignment.get('due_at')}")
            print(f"        [UPDATED] Assignment lock_at:   {updated_assignment.get('lock_at')}\n")
        else:
            print("        No linked assignment to update.\n")


if __name__ == "__main__":
    main()