#!/usr/bin/env python3
"""
List rubric associations for assignments in the configured Canvas course.

Reads etc/config.txt [canvas-lms-test] for COURSE_ID, API_TOKEN, CANVAS_DOMAIN_URL.
Prints assignment id/name and any attached rubric ids (from rubric_association or rubric include).
"""

import configparser
import requests
from typing import Dict, List, Any

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

config = configparser.ConfigParser()
config.read(CONFIG_PATH)
if CONFIG_SECTION not in config:
    raise SystemExit(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. Available: {config.sections()}"
    )

COURSE_ID = config[CONFIG_SECTION]["COURSE_ID"]
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"].rstrip("/")


def headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}


def list_assignments() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/assignments"
    params = {"per_page": 100, "include[]": ["rubric_association", "rubric"]}
    while url:
        resp = requests.get(url, headers=headers(), params=params, timeout=30)
        resp.raise_for_status()
        items.extend(resp.json())

        next_url = None
        link = resp.headers.get("Link", "")
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                next_url = part[part.find("<") + 1 : part.find(">")]
                break
        url = next_url
        params = {}
    return items


def extract_rubric_ids(assignment: Dict[str, Any]) -> List[str]:
    ids: List[str] = []
    ra = assignment.get("rubric_association")
    if isinstance(ra, dict):
        rid = ra.get("rubric_id") or ra.get("id")
        if rid:
            ids.append(str(rid))
    rub = assignment.get("rubric")
    if isinstance(rub, dict):
        rid = rub.get("id")
        if rid:
            ids.append(str(rid))
    elif isinstance(rub, list):
        for crit in rub:
            cid = crit.get("id")
            if cid:
                ids.append(str(cid))
    return list(dict.fromkeys(ids))  # dedupe


def main():
    assignments = list_assignments()
    print(f"Assignments scanned: {len(assignments)}")
    for a in assignments:
        rid_list = extract_rubric_ids(a)
        if rid_list:
            print(f"- assignment_id={a.get('id')} name='{a.get('name')}' rubrics={rid_list}")


if __name__ == "__main__":
    main()
