#!/usr/bin/env python3
"""
Update ONE Canvas discussion topic at a time using a JSON payload file.

Typical flow:
  1) You identify the discussion by title (or provide topic_id directly).
  2) Script loads the payload for a given module number (1-10).
  3) Script updates discussion_topic[message] via Canvas API.

Requirements:
  pip install requests

Auth:
  export CANVAS_TOKEN="..."
  export CANVAS_BASE_URL="https://your-school.instructure.com"   # no trailing slash
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import requests


def die(msg: str, code: int = 2) -> None:
    print(f"[!] {msg}", file=sys.stderr)
    sys.exit(code)


def load_payload(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        die("Payload JSON must be a list of objects.")
    return data


def pick_module(payload: List[Dict[str, Any]], module_num: int) -> Dict[str, Any]:
    for item in payload:
        if int(item.get("module", -1)) == module_num:
            return item
    die(f"Module {module_num} not found in payload.")


def canvas_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def find_discussion_topic_id(
    base_url: str, course_id: str, token: str, title: str
) -> Optional[int]:
    """
    Canvas: GET /api/v1/courses/:course_id/discussion_topics?search_term=...
    Returns first exact title match if found; else first partial match.
    """
    url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics"
    params = {"per_page": 100, "search_term": title}
    r = requests.get(url, headers=canvas_headers(token), params=params, timeout=30)
    if r.status_code != 200:
        die(f"Failed to search discussion topics ({r.status_code}): {r.text[:500]}")
    topics = r.json()
    if not isinstance(topics, list) or not topics:
        return None

    # exact match first
    for t in topics:
        if str(t.get("title", "")).strip().lower() == title.strip().lower():
            return int(t["id"])

    # else first result
    return int(topics[0]["id"])


def update_discussion(
    base_url: str, course_id: str, token: str, topic_id: int, message_html: str
) -> Dict[str, Any]:
    """
    Canvas: PUT /api/v1/courses/:course_id/discussion_topics/:topic_id
    Form fields:
      discussion_topic[message] = "<html...>"
    """
    url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics/{topic_id}"
    data = {"discussion_topic[message]": message_html}

    payload = {"message": message_html}
    r = requests.put(url, headers={**canvas_headers(token), "Content-Type": "application/json"}, json=payload, timeout=30)

    #r = requests.put(url, headers=canvas_headers(token), data=data, timeout=30)
    if r.status_code not in (200, 201):
        die(f"Update failed ({r.status_code}): {r.text[:800]}")
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Update ONE Canvas discussion board at a time from a JSON payload."
    )
    ap.add_argument("--course-id", required=True, help="Canvas course ID (numeric).")
    ap.add_argument("--module", type=int, required=True, choices=range(1, 11),
                    help="Module number 1-10 to select discussion content from payload JSON.")
    ap.add_argument("--payload", default="pentest_discussions_payload.json",
                    help="Path to payload JSON file.")
    ap.add_argument("--topic-id", type=int, default=None,
                    help="If provided, update this topic_id directly (skips search by title).")
    ap.add_argument("--title", default=None,
                    help="Discussion title to search (defaults to the title in payload for that module).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be updated without calling Canvas.")
    args = ap.parse_args()

    token = os.getenv("CANVAS_TOKEN")
    base_url = os.getenv("CANVAS_BASE_URL")
    if not token:
        die("Missing CANVAS_TOKEN env var.")
    if not base_url:
        die("Missing CANVAS_BASE_URL env var (e.g., https://school.instructure.com).")
    base_url = base_url.rstrip("/")

    payload = load_payload(args.payload)
    item = pick_module(payload, args.module)

    title = args.title or item.get("discussion_title")
    if not title:
        die("No discussion title available (provide --title).")

    message_html = item.get("message_html")
    if not message_html:
        die("No message_html in payload item.")

    topic_id = args.topic_id
    if topic_id is None:
        topic_id = find_discussion_topic_id(base_url, args.course_id, token, title)
        if topic_id is None:
            die(f"Could not find a discussion topic matching title: {title!r}")

    if args.dry_run:
        print(f"[DRY RUN] Would update course_id={args.course_id} topic_id={topic_id} title={title!r}")
        print(message_html)
        return

    updated = update_discussion(base_url, args.course_id, token, topic_id, message_html)
    print(f"[+] Updated: {updated.get('title')} (id={updated.get('id')})")


if __name__ == "__main__":
    main()
