#!/usr/bin/env python3
"""
Append "Goal 1: Explore planning and scoping." as a rubric criterion via Canvas API.

Defaults:
- Reads Canvas config from etc/config.txt section [canvas-lms-test]
- Targets a single rubric (set RUBRIC_ID below)
- Adds one criterion with two ratings (Meets / Incomplete)
- Starts in DRY_RUN mode to preview payload without updating Canvas

API docs: https://developerdocs.instructure.com/services/canvas/resources/rubrics
"""

import configparser
import requests
from typing import Dict, List

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

# If RUBRIC_ID is left blank, we will look for (or create) a rubric with this title.
RUBRIC_ID = "66415"
GOAL_RUBRIC_TITLE = "Course Goals / Objectives / Competencies"

DRY_RUN = True

GOAL_DESCRIPTION = "Goal 1: Explore planning and scoping."
GOAL_LONG_DESCRIPTION = "Explore planning and scoping."
GOAL_POINTS = 5

# Ratings for the new criterion
RATINGS = [
    {"description": "Meets goal", "points": GOAL_POINTS},
    {"description": "Incomplete", "points": 0},
]

config = configparser.ConfigParser()
config.read(CONFIG_PATH)
if CONFIG_SECTION not in config:
    raise SystemExit(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

COURSE_ID = config[CONFIG_SECTION]["COURSE_ID"]
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"].rstrip("/")


def headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}


def fetch_rubric(rubric_id: str) -> Dict:
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics/{rubric_id}"
    params = {"include[]": "criteria"}
    resp = requests.get(url, headers=headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def list_rubrics() -> List[Dict]:
    rubrics: List[Dict] = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics"
    params = {"per_page": 100, "include[]": "criteria"}
    while url:
        resp = requests.get(url, headers=headers(), params=params)
        resp.raise_for_status()
        rubrics.extend(resp.json())

        next_url = None
        link = resp.headers.get("Link", "")
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                next_url = part[part.find("<") + 1: part.find(">")]
                break

        url = next_url
        params = {}
    return rubrics


def extract_criteria(rubric: Dict) -> List[Dict]:
    if "criteria" in rubric:
        return rubric.get("criteria", [])
    if "data" in rubric and isinstance(rubric["data"], dict):
        return rubric["data"].get("criteria", [])
    return []


def criterion_already_present(criteria: List[Dict]) -> bool:
    target = GOAL_DESCRIPTION.lower()
    return any(target in (c.get("description", "").lower()) for c in criteria)


def build_payload(criteria: List[Dict], rubric_meta: Dict) -> Dict:
    data: Dict[str, str] = {}

    # Preserve rubric metadata when available
    title = rubric_meta.get("title") or rubric_meta.get("data", {}).get("title")
    if title:
        data["rubric[title]"] = title
    if "free_form_criterion_comments" in rubric_meta:
        data["rubric[free_form_criterion_comments]"] = rubric_meta.get(
            "free_form_criterion_comments", False
        )

    all_criteria = list(criteria)
    all_criteria.append(
        {
            "description": GOAL_DESCRIPTION,
            "long_description": GOAL_LONG_DESCRIPTION,
            "points": GOAL_POINTS,
            "ratings": RATINGS,
        }
    )

    for i, crit in enumerate(all_criteria):
        data[f"rubric[criteria][{i}][description]"] = crit.get("description", "")
        data[f"rubric[criteria][{i}][long_description]"] = crit.get("long_description", "")
        data[f"rubric[criteria][{i}][points]"] = crit.get("points", 0)

        # Preserve existing criterion IDs when present
        if crit.get("id"):
            data[f"rubric[criteria][{i}][criterion_id]"] = crit["id"]

        ratings = crit.get("ratings", [])
        for j, rating in enumerate(ratings):
            data[f"rubric[criteria][{i}][ratings][{j}][description]"] = rating.get("description", "")
            data[f"rubric[criteria][{i}][ratings][{j}][points]"] = rating.get("points", 0)
            # Preserve rating IDs when present
            if rating.get("id"):
                data[f"rubric[criteria][{i}][ratings][{j}][id]"] = rating["id"]

    return data


def update_rubric(rubric_id: str, payload: Dict) -> Dict:
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics/{rubric_id}"
    resp = requests.put(url, headers=headers(), data=payload)
    resp.raise_for_status()
    return resp.json()


def create_rubric_with_goal(title: str) -> Dict:
    payload: Dict[str, str] = {
        "rubric[title]": title,
        "rubric[free_form_criterion_comments]": False,
        "rubric[criteria][0][description]": GOAL_DESCRIPTION,
        "rubric[criteria][0][long_description]": GOAL_LONG_DESCRIPTION,
        "rubric[criteria][0][points]": GOAL_POINTS,
    }

    for j, rating in enumerate(RATINGS):
        payload[f"rubric[criteria][0][ratings][{j}][description]"] = rating.get("description", "")
        payload[f"rubric[criteria][0][ratings][{j}][points]"] = rating.get("points", 0)

    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics"
    resp = requests.post(url, headers=headers(), data=payload)
    resp.raise_for_status()
    return resp.json()


def main():
    rubric_id = RUBRIC_ID
    rubric = None

    # Resolve rubric: use provided ID, else search by title, else create (if not dry-run)
    if rubric_id:
        print(f"Fetching rubric {rubric_id} in course {COURSE_ID}...")
        rubric = fetch_rubric(rubric_id)
    else:
        print(f"No RUBRIC_ID provided; searching for '{GOAL_RUBRIC_TITLE}'...")
        rubrics = list_rubrics()
        for r in rubrics:
            title = r.get("title") or r.get("data", {}).get("title", "")
            if title and title.lower() == GOAL_RUBRIC_TITLE.lower():
                rubric = r
                rubric_id = r.get("id")
                break

        if rubric is None:
            if DRY_RUN:
                raise SystemExit(
                    "RUBRIC_ID not set and rubric not found. Set RUBRIC_ID or disable DRY_RUN to create it."
                )
            print(f"Rubric not found. Creating '{GOAL_RUBRIC_TITLE}' with Goal 1 criterion...")
            created = create_rubric_with_goal(GOAL_RUBRIC_TITLE)
            print(f"Created rubric id={created.get('id')} title='{created.get('title')}'")
            return

    if not rubric_id:
        raise SystemExit("Could not resolve rubric id.")

    print(f"Using rubric {rubric_id} in course {COURSE_ID}...")
    if rubric is None:
        rubric = fetch_rubric(rubric_id)
    criteria = extract_criteria(rubric)

    if criterion_already_present(criteria):
        raise SystemExit("Goal criterion already present; no update needed.")

    payload = build_payload(criteria, rubric)

    if DRY_RUN:
        print("DRY RUN: not updating Canvas. Payload preview:\n")
        for k, v in payload.items():
            print(f"{k} = {v}")
        return

    print("Updating rubric with new criterion...")
    updated = update_rubric(rubric_id, payload)
    print(f"Updated rubric: {updated.get('title', 'rubric updated')}")


if __name__ == "__main__":
    main()
