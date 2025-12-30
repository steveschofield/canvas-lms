#!/usr/bin/env python3
"""Update a Canvas course late policy to auto-grade missing work.

This script enables "Automatically apply grade for missing submissions". By
default it sets missing submissions to 0% of the possible points (i.e., full
deduction). Adjust `GRADE_FOR_MISSING_PERCENT` if you want a different default.

Config: etc/config.txt with section [canvas-lms-test]
Required keys: COURSE_ID, API_TOKEN, CANVAS_DOMAIN_URL
"""

import configparser
import json
from typing import Any, Dict

import requests

CONFIG_PATH = "/Users/ss/etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

# Late policy settings
# Default: set missing submissions to 0% of possible points
GRADE_FOR_MISSING_PERCENT = 0
MISSING_DEDUCTION_PERCENT = 100 - GRADE_FOR_MISSING_PERCENT  # Canvas expects deduction percent
LATE_MINIMUM_PERCENT = 0
DISABLE_LATE_DEDUCTION = True  # keep late submission penalties off


def canvas_headers(api_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def late_policy_url(canvas_domain_url: str, course_id: str) -> str:
    base = canvas_domain_url.rstrip("/")
    if not base.startswith("http"):
        base = f"https://{base}"
    return f"{base}/api/v1/courses/{course_id}/late_policy"


def get_late_policy(course_id: str, api_token: str, canvas_domain_url: str) -> Dict[str, Any]:
    url = late_policy_url(canvas_domain_url, course_id)
    response = requests.get(url, headers=canvas_headers(api_token))
    response.raise_for_status()
    return response.json()


def set_auto_zero_late_policy(course_id: str, api_token: str, canvas_domain_url: str) -> Dict[str, Any]:
    url = late_policy_url(canvas_domain_url, course_id)
    payload = {
        "late_policy": {
            "missing_submission_deduction_enabled": True,
            # Canvas stores a deduction percent; 100 means grade = 0% of possible.
            "missing_submission_deduction": MISSING_DEDUCTION_PERCENT,
            "late_submission_minimum_percent": LATE_MINIMUM_PERCENT,
        }
    }

    if DISABLE_LATE_DEDUCTION:
        payload["late_policy"]["late_submission_deduction_enabled"] = False

    response = requests.put(url, headers=canvas_headers(api_token), json=payload)
    response.raise_for_status()
    return response.json()


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if CONFIG_SECTION not in config:
        raise KeyError(f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}")
    return config[CONFIG_SECTION]


def pretty_print_policy(label: str, policy: Dict[str, Any]) -> None:
    key_fields = {
        "missing_submission_deduction_enabled": policy.get("missing_submission_deduction_enabled"),
        "missing_submission_deduction": policy.get("missing_submission_deduction"),
        "late_submission_deduction_enabled": policy.get("late_submission_deduction_enabled"),
        "late_submission_deduction": policy.get("late_submission_deduction"),
        "late_submission_interval": policy.get("late_submission_interval"),
        "late_submission_minimum_percent": policy.get("late_submission_minimum_percent"),
    }
    print(f"{label}: {json.dumps(key_fields, indent=2, sort_keys=True)}")


def main():
    cfg = load_config()
    course_id = cfg["COURSE_ID"]
    api_token = cfg["API_TOKEN"]
    canvas_domain_url = cfg["CANVAS_DOMAIN_URL"]

    print(f"Updating late policy for course {course_id} to auto-zero missing submissions.\n")

    try:
        current_policy = get_late_policy(course_id, api_token, canvas_domain_url)
        pretty_print_policy("Current policy", current_policy)
    except requests.HTTPError as exc:  # Canvas returns 404 if policy not set yet
        if exc.response.status_code == 404:
            print("No existing late policy found; a new policy will be created.")
        else:
            raise

    updated_policy = set_auto_zero_late_policy(course_id, api_token, canvas_domain_url)
    pretty_print_policy("Updated policy", updated_policy)


if __name__ == "__main__":
    main()
