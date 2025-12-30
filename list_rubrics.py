#!/usr/bin/env python3
"""
List all rubrics in the configured Canvas course.

Reads etc/config.txt section [canvas-lms-test] for:
  COURSE_ID, API_TOKEN, CANVAS_DOMAIN_URL

Prints: rubric id, title, points_possible, association_count (if provided),
first criterion id/points/rating ids for quick inspection.
"""

import configparser
import requests
from typing import Dict, List

CONFIG_PATH = "/Users/ss/etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

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


def list_rubrics() -> List[Dict]:
    rubrics: List[Dict] = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics"
    params = {"per_page": 100}
    while url:
        resp = requests.get(url, headers=headers(), params=params, timeout=30)
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


def main():
    rubrics = list_rubrics()
    print(f"Found {len(rubrics)} rubrics in course {COURSE_ID}:")
    for rb in rubrics:
        rid = rb.get("id")
        title = rb.get("title")
        points = rb.get("points_possible")
        assoc = rb.get("association_count")
        crits = rb.get("data") or rb.get("criteria") or []
        first = crits[0] if crits else {}
        cid = first.get("id")
        cpoints = first.get("points")
        rating_ids = [r.get("id") for r in first.get("ratings", [])] if first else []
        print(
            f"- id={rid} title='{title}' points={points} assoc={assoc} "
            f"first_criterion={cid} crit_points={cpoints} rating_ids={rating_ids}"
        )


if __name__ == "__main__":
    main()
