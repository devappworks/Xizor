# tools/freedcamp_api.py
"""Freedcamp task‑creation helper (public API v1) — resilient to every response shape I’ve seen.

Usage
-----
>>> create_freedcamp_task(
        title="Hello",
        description="World",
        assignee_id=123,
        priority="P1",
        due_date="2025-05-20",
    )
Returns a dict:
    {
        "success": True,
        "task_id": "64820671",
        "task_url": "https://freedcamp.com/view/3590973/tasks/64820671",
        "error": None,
        "response": {...raw task json...},
    }
"""

from __future__ import annotations

import os
import time
import hmac
import hashlib
import json
import logging
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# config / logging
# ---------------------------------------------------------------------------
load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

API_KEY       = os.getenv("FREEDCAMP_API_KEY")
API_SECRET    = os.getenv("FREEDCAMP_API_SECRET")
PROJECT_ID    = os.getenv("FREEDCAMP_PROJECT_ID")
TASKGROUP_ID  = os.getenv("FREEDCAMP_TASK_GROUP_ID")  # task‑list id

BASE_URL = "https://freedcamp.com/api/v1"

PRIO_MAP: dict[str, int] = {"P0": 3, "P1": 2, "P2": 1}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _auth() -> Dict[str, str]:
    if not API_KEY or not API_SECRET:
        raise RuntimeError("FREEDCAMP_API_KEY or FREEDCAMP_API_SECRET not set in .env")

    ts  = str(int(time.time()))
    sig = hmac.new(API_SECRET.encode(), f"{API_KEY}{ts}".encode(), hashlib.sha1).hexdigest()
    return {"api_key": API_KEY, "timestamp": ts, "hash": sig}


# ---------------------------------------------------------------------------
# public entry‑point
# ---------------------------------------------------------------------------

def create_freedcamp_task(
    *,
    title: str,
    description: str,
    assignee_id: int = 0,
    priority: str = "P2",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a task in Freedcamp and return a dict with results."""

    if not all([API_KEY, API_SECRET, PROJECT_ID, TASKGROUP_ID]):
        return {"success": False, "error": "Missing API credentials or project/task‑group IDs"}

    payload: dict[str, Any] = {
        "project_id": PROJECT_ID,
        "task_group_id": TASKGROUP_ID,
        "title": title,
        "description": description,
        "assigned_to_id": assignee_id,
        "priority": PRIO_MAP.get(priority, 2),
    }
    if due_date:
        payload["due_date"] = due_date  # YYYY‑MM‑DD

    logger.debug("[FC‑REQ] %s", json.dumps(payload, indent=2))

    try:
        res = requests.post(
            f"{BASE_URL}/tasks",
            params=_auth(),
            files={"data": (None, json.dumps(payload))},
            timeout=15,
        )
        res.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Freedcamp API HTTP error: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Parse the JSON.  Freedcamp can return:
    #   1) {"data": { ...task... }}
    #   2) {"tasks": [ ...task... ]}
    #   3) {"data": {"tasks": [ ...task... ]}}
    # ------------------------------------------------------------------
    try:
        resp_json: dict[str, Any] = res.json()
    except ValueError:
        logger.error("Freedcamp returned non‑JSON body: %s", res.text[:200])
        return {"success": False, "error": "Invalid JSON in API response"}

    logger.info("Freedcamp response: %s", resp_json)

    task_item: Optional[dict[str, Any]] = None

    if isinstance(resp_json.get("data"), dict):
        inner = resp_json["data"]
        if "id" in inner or "task_id" in inner:
            task_item = inner  # case 1
        elif isinstance(inner.get("tasks"), list) and inner["tasks"]:  # case 3
            task_item = inner["tasks"][0]
    elif isinstance(resp_json.get("tasks"), list) and resp_json["tasks"]:  # case 2
        task_item = resp_json["tasks"][0]

    if not task_item:
        return {"success": False, "error": "Unexpected Freedcamp response format", "response": resp_json}

    task_id  = task_item.get("id") or task_item.get("task_id")
    task_url = task_item.get("url")
    if task_id and not task_url:
        task_url = f"https://freedcamp.com/view/{PROJECT_ID}/tasks/{task_id}"

    return {
        "success": bool(task_id),
        "task_id": str(task_id) if task_id else None,
        "task_url": task_url,
        "error": None if task_id else "No task ID in response",
        "response": task_item,
    }
