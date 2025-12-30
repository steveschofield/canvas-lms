#!/usr/bin/env python3
"""Set per-assignment gradebook posting policy.

Uses the Canvas endpoint:
  PUT /api/v1/courses/:course_id/assignments/:assignment_id/gradebook_settings

Default behavior: enable manual posting (`post_manually = True`) so grades and
late/missing visibility stay hidden until you post them. Override with
`--auto` to return to automatic posting.

Config: /Users/ss/etc/config.txt, section [canvas-lms-test]
Required keys: COURSE_ID, API_TOKEN, CANVAS_DOMAIN_URL
"""

import argparse
import configparser
from typing import Any, Dict

import requests

CONFIG_PATH = "/Users/ss/etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"


def canvas_headers(api_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def gradebook_settings_url(canvas_domain_url: str, course_id: str, assignment_id: str) -> str:
    base = canvas_domain_url.rstrip("/")
    if not base.startswith("http"):
        base = f"https://{base}"
    return f"{base}/api/v1/courses/{course_id}/assignments/{assignment_id}/gradebook_settings"


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if CONFIG_SECTION not in config:
        raise KeyError(f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}")
    return config[CONFIG_SECTION]


def get_gradebook_settings(course_id: str, assignment_id: str, api_token: str, canvas_domain_url: str) -> Dict[str, Any]:
    url = gradebook_settings_url(canvas_domain_url, course_id, assignment_id)
    resp = requests.get(url, headers=canvas_headers(api_token))
    resp.raise_for_status()
    return resp.json()


def update_gradebook_settings(course_id: str, assignment_id: str, api_token: str, canvas_domain_url: str, post_manually: bool) -> Dict[str, Any]:
    url = gradebook_settings_url(canvas_domain_url, course_id, assignment_id)
    payload = {"gradebook_setting": {"post_manually": post_manually}}
    resp = requests.put(url, headers=canvas_headers(api_token), json=payload)
    resp.raise_for_status()
    return resp.json()


def parse_args():
    parser = argparse.ArgumentParser(description="Set per-assignment posting policy")
    parser.add_argument("assignment_id", help="Assignment ID to update")
    parser.add_argument("--course-id", dest="course_id", help="Override course ID from config")
    parser.add_argument("--auto", action="store_true", help="Use automatic posting (post_manually = False)")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config()

    course_id = args.course_id or cfg["COURSE_ID"]
    assignment_id = args.assignment_id
    api_token = cfg["API_TOKEN"]
    canvas_domain_url = cfg["CANVAS_DOMAIN_URL"]

    target_post_manually = not args.auto

    print(f"Setting assignment {assignment_id} in course {course_id} to post_manually={target_post_manually}\n")

    current = get_gradebook_settings(course_id, assignment_id, api_token, canvas_domain_url)
    print(f"Current settings: {current}")

    updated = update_gradebook_settings(course_id, assignment_id, api_token, canvas_domain_url, target_post_manually)
    print(f"Updated settings: {updated}")


if __name__ == "__main__":
    main()
