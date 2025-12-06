#!/usr/bin/env python3
"""
Automatically update Canvas assignment dates based on the chapter number found
at the start of the assignment title.

Example assignment names:
    "1.1.1 Introduction"
    "1.2.3 Lab"
    "2.1.1 Assessment"
    "5.3.2 Activity"

Rule:
    The chapter number = the FIRST number before the first dot.

All assignments sharing the same chapter number receive the same:
    unlock_at (Available From)
    due_at    (Due Date)
    lock_at   (Available Until)
"""

import configparser
import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo  # NEW: for DST-aware timestamps

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

YEAR = 2026
TIMEZONE = ZoneInfo("America/Detroit")  # NEW: use real timezone, not fixed offset
AVAILABLE_TIME = "00:00:00"
DUE_TIME = "23:59:00"

DRY_RUN = False  # flip to True for testing if you want

# Per-chapter dates (chapter N == module N)
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
    raise KeyError(f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}")

COURSE_ID = int(config[CONFIG_SECTION]["COURSE_ID"])
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"].rstrip("/")


# --------------------------------------------------------------------
# Canvas helpers
# --------------------------------------------------------------------

def canvas_headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}


def list_assignments(course_id):
    assignments = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/assignments"
    params = {"per_page": 100}

    while url:
        r = requests.get(url, headers=canvas_headers(), params=params)
        r.raise_for_status()
        assignments.extend(r.json())

        next_url = None
        link = r.headers.get("Link", "")
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                next_url = part[part.find("<") + 1: part.find(">")]
                break

        url = next_url
        params = {}

    return assignments


def update_assignment_dates(course_id, assignment_id, unlock_at, due_at):
    payload = {
        "assignment[unlock_at]": unlock_at,
        "assignment[due_at]": due_at,
        "assignment[lock_at]": due_at,  # Available Until = Due Date
    }
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    r = requests.put(url, headers=canvas_headers(), data=payload)
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------
# Helper: build Canvas ISO timestamp (DST-aware)
# --------------------------------------------------------------------

def build_iso(date_str, time_str):
    """
    date_str '1/12', time_str '23:59:00' ->
    '2026-01-12T23:59:00-05:00' (or -04:00 after DST starts)
    """
    month, day = map(int, date_str.split("/"))
    hour, minute, second = map(int, time_str.split(":"))
    dt = datetime(YEAR, month, day, hour, minute, second, tzinfo=TIMEZONE)
    # Canvas accepts full ISO8601 with offset; this will include -05:00 or -04:00 as appropriate
    return dt.isoformat(timespec="seconds")


# --------------------------------------------------------------------
# Extract chapter number from assignment name
# --------------------------------------------------------------------

def extract_chapter_number(title):
    """
    Returns the leading integer from patterns like:
      1.1.1 Something
      10.2.3 Activity
      3.0 Quiz

    Returns None if no match.
    """
    m = re.match(r"^(\d+)\.", title.strip())
    if m:
        return int(m.group(1))
    return None


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    print(f"Updating assignments for COURSE_ID={COURSE_ID} (DRY_RUN={DRY_RUN})\n")

    assignments = list_assignments(COURSE_ID)

    for a in assignments:
        name = a.get("name", "")
        assignment_id = a.get("id")

        chapter = extract_chapter_number(name)
        if chapter is None:
            print(f"[SKIP] '{name}' → no chapter prefix found.")
            continue

        if chapter not in DATES:
            print(f"[SKIP] '{name}' → chapter {chapter} not in DATES table.")
            continue

        # Get dates for this chapter
        date_info = DATES[chapter]
        available_str = date_info["available"]
        due_str = date_info["due"]

        # Convert to ISO8601 (DST-aware)
        unlock_at_iso = build_iso(available_str, AVAILABLE_TIME)
        due_at_iso = build_iso(due_str, DUE_TIME)

        print(f"[MATCH] '{name}' → Chapter {chapter}")
        print(f"        Available From:  {unlock_at_iso}")
        print(f"        Due Date:        {due_at_iso}")
        print(f"        Available Until: {due_at_iso}")

        if DRY_RUN:
            print("        (DRY RUN: no changes applied)\n")
            continue

        updated = update_assignment_dates(COURSE_ID, assignment_id, unlock_at_iso, due_at_iso)
        print(f"        [UPDATED] unlock_at: {updated.get('unlock_at')}")
        print(f"        [UPDATED] due_at:   {updated.get('due_at')}")
        print(f"        [UPDATED] lock_at:  {updated.get('lock_at')}\n")


if __name__ == "__main__":
    main()