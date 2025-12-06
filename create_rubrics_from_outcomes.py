#!/usr/bin/env python3
"""
Create one rubric per course outcome, using the outcome's title as the rubric title
and copying the outcome's ratings/points into a single criterion.

Defaults:
- Reads Canvas config from etc/config.txt, section [canvas-lms-test].
- DRY_RUN=True: prints the rubrics it would create; no API writes until flipped.
- Skips any rubric whose title already exists in the course.

API endpoints used:
- GET  /api/v1/courses/:course_id/outcome_groups
- GET  /api/v1/outcome_groups/:outcome_group_id/outcomes?include[]=ratings
- GET  /api/v1/courses/:course_id/rubrics
- POST /api/v1/courses/:course_id/rubrics

Adjust constants below if you need a different config section or a subset of outcomes.
"""

import configparser
import requests
from typing import Dict, List, Set
from functools import lru_cache

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"
DRY_RUN = False

# If you want to only process certain outcomes, list their IDs here; leave empty to process all.
LIMIT_TO_OUTCOME_IDS: List[int] = []

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


def list_outcome_groups() -> List[Dict]:
    groups: List[Dict] = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/outcome_groups"
    params = {"per_page": 100}
    while url:
        resp = requests.get(url, headers=headers(), params=params, timeout=30)
        resp.raise_for_status()
        groups.extend(resp.json())

        next_url = None
        link = resp.headers.get("Link", "")
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                next_url = part[part.find("<") + 1: part.find(">")]
                break
        url = next_url
        params = {}
    return groups


def list_outcomes_from_groups(groups: List[Dict]) -> List[Dict]:
    seen_ids: Set[int] = set()
    outcomes: List[Dict] = []

    for g in groups:
        group_id = g.get("id")
        if not group_id:
            continue
        url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/outcome_groups/{group_id}/outcomes"
        params = {"per_page": 100}
        while url:
            resp = requests.get(url, headers=headers(), params=params, timeout=30)
            if resp.status_code == 404:
                break
            resp.raise_for_status()
            items = resp.json()
            for o in items:
                outcome = o.get("outcome") or o
                oid = outcome.get("id") if isinstance(outcome, dict) else None
                if oid and oid not in seen_ids:
                    seen_ids.add(oid)
                    outcomes.append(outcome)
            next_url = None
            link = resp.headers.get("Link", "")
            for part in link.split(","):
                part = part.strip()
                if 'rel="next"' in part:
                    next_url = part[part.find("<") + 1: part.find(">")]
                    break
            url = next_url
            params = {}

    return outcomes


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


def rubric_exists(title: str, rubrics: List[Dict]) -> bool:
    return any((r.get("title") or r.get("data", {}).get("title", "")).lower() == title.lower() for r in rubrics)


@lru_cache(maxsize=None)
def fetch_outcome(outcome_id: int) -> Dict:
    url = f"{CANVAS_DOMAIN_URL}/api/v1/outcomes/{outcome_id}"
    params = {"include[]": "ratings"}
    resp = requests.get(url, headers=headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def enrich_outcome(outcome: Dict) -> Dict:
    oid = outcome.get("id")
    if not oid:
        return outcome
    detailed = fetch_outcome(int(oid))
    merged = dict(outcome)
    merged.update(detailed)
    return merged


def ratings_from_outcome(outcome: Dict) -> List[Dict]:
    ratings = outcome.get("ratings") or []
    if ratings:
        return [
            {
                "description": r.get("description", ""),
                "points": r.get("points", 0),
            }
            for r in ratings
        ]
    # fallback two-level rubric
    return [
        {"description": "Meets", "points": 5},
        {"description": "Incomplete", "points": 0},
    ]


def points_from_ratings(ratings: List[Dict]) -> float:
    if not ratings:
        return 0
    return max((r.get("points", 0) for r in ratings), default=0)


def build_payload(outcome: Dict) -> Dict[str, str]:
    title = outcome.get("title", "Outcome Rubric")
    long_desc = outcome.get("description") or outcome.get("display_name") or title
    ratings = ratings_from_outcome(outcome)
    points = points_from_ratings(ratings)

    payload: Dict[str, str] = {
        "rubric[title]": title,
        "rubric[free_form_criterion_comments]": False,
        "rubric[criteria][0][description]": title,
        "rubric[criteria][0][long_description]": long_desc,
        "rubric[criteria][0][points]": points,
    }

    for idx, rating in enumerate(ratings):
        payload[f"rubric[criteria][0][ratings][{idx}][description]"] = rating.get("description", "")
        payload[f"rubric[criteria][0][ratings][{idx}][points]"] = rating.get("points", 0)

    return payload


def create_rubric(payload: Dict) -> Dict:
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics"
    resp = requests.post(url, headers=headers(), data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    print(f"Reading outcome groups for course {COURSE_ID}...")
    groups = list_outcome_groups()
    print(f"Found {len(groups)} outcome groups. Reading outcomes from groups...")
    outcomes = list_outcomes_from_groups(groups)
    # Enrich with ratings/description
    outcomes = [enrich_outcome(o) for o in outcomes]

    if LIMIT_TO_OUTCOME_IDS:
        outcomes = [o for o in outcomes if o.get("id") in LIMIT_TO_OUTCOME_IDS]
        print(f"Filtered to {len(outcomes)} outcomes via LIMIT_TO_OUTCOME_IDS")

    print(f"Found {len(outcomes)} outcomes. Loading existing rubrics for duplicate check...")
    rubrics = list_rubrics()

    to_create = []
    for o in outcomes:
        title = o.get("title", "").strip() or f"Outcome {o.get('id')}"
        if rubric_exists(title, rubrics):
            print(f"[SKIP] Rubric titled '{title}' already exists.")
            continue
        payload = build_payload(o)
        to_create.append((title, payload))

    if not to_create:
        print("No new rubrics to create. Done.")
        return

    print(f"Prepared {len(to_create)} new rubrics.")
    if DRY_RUN:
        print("DRY RUN: showing first payload (abbreviated) and titles...")
        for title, payload in to_create:
            print(f"Title: {title}")
            for k, v in payload.items():
                print(f"  {k} = {v}")
            print("---")
        return

    for title, payload in to_create:
        print(f"Creating rubric '{title}'...")
        created = create_rubric(payload)
        body = created.get("rubric") if isinstance(created, dict) else None
        rid = None
        rtitle = None
        if body:
            rid = body.get("id")
            rtitle = body.get("title")
        else:
            rid = created.get("id") if isinstance(created, dict) else None
            rtitle = created.get("title") if isinstance(created, dict) else None
        print(f"  Created rubric id={rid} title='{rtitle}'")


if __name__ == "__main__":
    main()
