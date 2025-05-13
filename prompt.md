### Step-by-step guide for implementing Freedcamp integration in **Cursor** (Agent SDK project)

> Follow every step in order. After each numbered section, commit your changes and run a local test.

---

## 1  Set up your environment

| Step    | Command / file                       | Notes                                                                                                                                                 |
| ------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1.1** | `pip install requests python-dotenv` | Add them to `requirements.txt` if they’re missing.                                                                                                    |
| **1.2** | **.env**                             | Add / update:<br>`FREEDCAMP_API_KEY=pk_xxx`<br>`FREEDCAMP_API_SECRET=sk_xxx`<br>`FREEDCAMP_PROJECT_ID=12345678`<br>`FREEDCAMP_TASK_GROUP_ID=87654321` |
| **1.3** | Cursor **Run Config**                | Point it to the same `.env` file so `uvicorn` loads the vars automatically.                                                                           |

---

## 2  Create `freedcamp_api.py`

1. In `src/tools/`, add **`freedcamp_api.py`**.
2. Paste the patched code (HMAC-SHA1 auth, `create_freedcamp_task`, etc.):

```python
# src/tools/freedcamp_api.py
import os, time, hmac, hashlib, json, logging, requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from agents import function_tool

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY      = os.getenv("FREEDCAMP_API_KEY")
API_SECRET   = os.getenv("FREEDCAMP_API_SECRET")
PROJECT_ID   = os.getenv("FREEDCAMP_PROJECT_ID")
TASKGROUP_ID = os.getenv("FREEDCAMP_TASK_GROUP_ID")

BASE_URL = "https://freedcamp.com/api/v1"

def _auth() -> Dict[str, str]:
    ts = str(int(time.time()))
    signature = hmac.new(
        API_SECRET.encode(),
        f"{API_KEY}{ts}".encode(),
        hashlib.sha1,
    ).hexdigest()
    return {"api_key": API_KEY, "timestamp": ts, "hash": signature}

PRIO_MAP = {"P0": 3, "P1": 2, "P2": 1}

@function_tool
def create_freedcamp_task(
    title: str,
    description: str,
    assignee_id: int = 0,
    priority: str = "P2",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a task in Freedcamp."""
    if not (API_KEY and API_SECRET and PROJECT_ID and TASKGROUP_ID):
        return {"success": False, "error": "Missing API creds or IDs"}

    payload = {
        "title": title,
        "description": description,
        "project_id": PROJECT_ID,
        "task_group_id": TASKGROUP_ID,
        "priority": PRIO_MAP.get(priority, 2),
        "assigned_to_id": assignee_id,
    }
    if due_date:
        payload["due_date"] = due_date  # already YYYY-MM-DD

    logger.debug("[FC-REQ]\n%s", json.dumps(payload, indent=2))

    res = requests.post(
        f"{BASE_URL}/tasks",
        params=_auth(),
        data={"data": json.dumps(payload)},   # form-data field “data”
    )
    if res.ok:
        data = res.json().get("data", {})
        task_id = data.get("id")
        return {
            "success": True,
            "task_id": task_id,
            "task_url": f"https://freedcamp.com/view/{PROJECT_ID}/tasks/{task_id}",
            "response": data,
        }
    return {"success": False, "error": res.text, "status": res.status_code}
```

---

## 3  Map Slack → Freedcamp user IDs

Create (or update) a small mapping module:

```python
# src/user_map.py
SLACK_TO_FC = {
    "@aleks": 11223344,
    "@petar": 55667788,
}
```

In **`OrchestratorAgent`** (before calling `create_freedcamp_task`):

```python
from user_map import SLACK_TO_FC
assignee_id = SLACK_TO_FC.get(task_details.assignee.lower(), 0)  # 0 = unassigned
fc_result = create_freedcamp_task(
    title=task_details.title,
    description=task_details.description,
    assignee_id=assignee_id,
    priority=task_details.priority,
    due_date=task_details.due_date,
)
```

---

## 4  Update the agent

* Import the new tool:

  ```python
  from tools.freedcamp_api import create_freedcamp_task
  ```
* Ensure the tool is listed in `tools=[create_freedcamp_task]` for `OrchestratorAgent`.
* Confirm the priority map matches P0→3, P1→2, P2→1 (already in the helper).

---

## 5  Dependencies

Add to **requirements.txt**:

```
requests>=2.31
python-dotenv>=1.0
```

Cursor will prompt you to sync; accept.

---

## 6  Quick local smoke test

```bash
python - <<'PY'
from tools.freedcamp_api import create_freedcamp_task
print(create_freedcamp_task(
    title="Cursor smoke-test task",
    description="Testing Freedcamp API integration",
    assignee_id=0,
    priority="P1",
    due_date="2025-05-20"
))
PY
```

Expected output: `{"success": true, "task_id": …}`.
If you get 401/403, check `.env` values and system clock (timestamp is part of the HMAC).

---

## 7  End-to-end test via Slack

1. DM your Slack bot something like:

   > *Petar, please write unit tests for the Freedcamp integration by Friday.*
2. You should receive two bot replies:

   * “Task Details” (draft confirmation)
   * “Task created successfully in Freedcamp” with a link.
3. Open the link → verify the task is visible in Freedcamp.

---

## 8  Logging & debugging

Set logging to `DEBUG` while debugging:

```python
logging.basicConfig(level=logging.DEBUG)
```

Look for `[FC-REQ]` and any JSON error returned by Freedcamp.

---

## 9  Common errors

| API message                 | Likely cause                                    | Fix                                                     |
| --------------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| `Invalid hash`              | Wrong `api_secret` or system clock skew > 5 min | Sync system time (`ntpdate`)                            |
| `task_group_id is required` | Not provided                                    | Set `FREEDCAMP_TASK_GROUP_ID` and include it in payload |
| `assigned_to_id is invalid` | ID not part of the project                      | Retrieve user list with `GET /users` and update mapping |


Cursor’s CI (if configured) should run your tests automatically.