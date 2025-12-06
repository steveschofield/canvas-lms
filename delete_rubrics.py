#!/usr/bin/env python3
"""
Delete specified rubrics from the configured Canvas course.

Reads etc/config.txt section [canvas-lms-test] for:
  COURSE_ID, API_TOKEN, CANVAS_DOMAIN_URL

Edit RUBRIC_IDS below to control which rubrics to delete.
"""

import configparser
import requests
from typing import Dict, List

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"
# Rubric IDs to delete
RUBRIC_IDS: List[int] = [66415, 66416, 66418, 66419, 66420, 66421]

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


def delete_rubric(rubric_id: int) -> None:
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{COURSE_ID}/rubrics/{rubric_id}"
    resp = requests.delete(url, headers=headers(), timeout=30)
    if resp.status_code not in (200, 202, 204):
        msg = resp.text.strip()
        raise SystemExit(f"Failed to delete rubric {rubric_id}: status {resp.status_code} body={msg}")


def main():
    for rid in RUBRIC_IDS:
        print(f"Deleting rubric {rid}...")
        try:
            delete_rubric(rid)
            print(f"  Deleted rubric {rid}")
        except SystemExit as e:
            print(e)
            continue


if __name__ == "__main__":
    main()
