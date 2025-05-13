"""
Fetch Task-group (Task-list) IDs from Freedcamp.

.env must contain:
  FREEDCAMP_API_KEY
  FREEDCAMP_API_SECRET
  FREEDCAMP_PROJECT_ID
"""

import os, time, hmac, hashlib, requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()  # ensure .env is loaded

API_KEY       = os.getenv("FREEDCAMP_API_KEY")
API_SECRET    = os.getenv("FREEDCAMP_API_SECRET")
PROJECT_ID    = os.getenv("FREEDCAMP_PROJECT_ID")

if not all([API_KEY, API_SECRET, PROJECT_ID]):
    raise RuntimeError("Missing Freedcamp creds or project ID in .env")

BASE_URL = "https://freedcamp.com/api/v1"


def _auth() -> Dict[str, str]:
    """Return api_key, timestamp, hash (HMAC-SHA1)."""
    ts = str(int(time.time()))
    sig = hmac.new(
        API_SECRET.encode(),
        f"{API_KEY}{ts}".encode(),
        hashlib.sha1,
    ).hexdigest()
    return {"api_key": API_KEY, "timestamp": ts, "hash": sig}


class FreedcampTaskGroups:
    APP_ID = 2  # Tasks application

    @staticmethod
    def list_raw(limit: int = 200, offset: int = 0) -> List[Dict]:
        """
        Return raw task-list objects:
        [{'id': '272', 'title': 'Back-end', ...}, …]
        """
        url = f"{BASE_URL}/lists/{FreedcampTaskGroups.APP_ID}"
        params = {
            **_auth(),
            "project_id": PROJECT_ID,
            "limit": limit,
            "offset": offset,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()

        return r.json().get("data", {}).get("lists", [])

    @staticmethod
    def id_map() -> Dict[str, str]:
        """Return {title_lower: id} for quick lookup."""
        return {lst["title"].lower(): lst["id"] for lst in FreedcampTaskGroups.list_raw()}


# quick CLI smoke-test ---------------------------------------------------------
if __name__ == "__main__":
    for lst in FreedcampTaskGroups.list_raw():
        print(f"{lst['id']:>8}  {lst['title']}")
