import os, time, hmac, hashlib, requests, logging
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
log = logging.getLogger(__name__)

class FreedcampUserFetcher:
    BASE_URL = "https://freedcamp.com/api/v1"

    def __init__(self):
        self.api_key    = os.getenv("FREEDCAMP_API_KEY")
        self.api_secret = os.getenv("FREEDCAMP_API_SECRET")
        if not (self.api_key and self.api_secret):
            raise RuntimeError("Missing FREEDCAMP_API_KEY / FREEDCAMP_API_SECRET")

    # ------------------------------------------------------------------ helpers
    def _auth(self) -> Dict[str, str]:
        ts = str(int(time.time()))
        sig = hmac.new(
            self.api_secret.encode(),
            f"{self.api_key}{ts}".encode(),
            digestmod="sha1",
        ).hexdigest()
        return {"api_key": self.api_key, "timestamp": ts, "hash": sig}

    # ------------------------------------------------------------------ public
    def list_users(self, limit: int = 200, offset: int = 0) -> List[Dict]:
        """Return raw Freedcamp user objects the key can see."""
        params = {**self._auth(), "limit": limit, "offset": offset}
        r = requests.get(f"{self.BASE_URL}/users", params=params, timeout=15)
        r.raise_for_status()

        payload = r.json()             # whole response
        users = payload.get("data", {}).get("users", [])
        log.debug("Fetched %s users", len(users))
        return users

    def id_map(self) -> Dict[str, int]:
        """Handy dict → {email_lower/full_name_lower : user_id}."""
        mapping: Dict[str, int] = {}
        for u in self.list_users():
            mapping[u["full_name"].lower()] = int(u["user_id"])
            if u.get("email"):
                mapping[u["email"].lower()] = int(u["user_id"])
        return mapping


# ------------------- smoke test ----------------------------------------------
if __name__ == "__main__":
    fc = FreedcampUserFetcher()
    for u in fc.list_users()[:5]:
        print(f"{u['user_id']:>8}  {u['full_name']}  <{u.get('email')}>")
