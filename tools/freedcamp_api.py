# tools/freedcamp_api.py
import os
import time
import hmac
import hashlib
import json
import logging
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

API_KEY = os.getenv("FREEDCAMP_API_KEY")
API_SECRET = os.getenv("FREEDCAMP_API_SECRET")
PROJECT_ID = os.getenv("FREEDCAMP_PROJECT_ID")
TASKGROUP_ID = os.getenv("FREEDCAMP_TASK_GROUP_ID")

BASE_URL = "https://freedcamp.com/api/v1"

def _auth() -> Dict[str, str]:
    """Generates authentication parameters for Freedcamp API."""
    if not API_KEY or not API_SECRET:
        logger.error("API_KEY or API_SECRET not configured.")
        raise ValueError("API_KEY or API_SECRET not configured for _auth.")
        
    ts = str(int(time.time()))
    signature = hmac.new(
        API_SECRET.encode('utf-8'), # Ensure encoding for hmac
        f"{API_KEY}{ts}".encode('utf-8'), # Ensure encoding for hmac
        hashlib.sha1,
    ).hexdigest()
    return {"api_key": API_KEY, "timestamp": ts, "hash": signature}

PRIO_MAP = {"P0": 3, "P1": 2, "P2": 1}

# Not decorated with @function_tool as per Prompt2.md
def create_freedcamp_task(
    title: str,
    description: str,
    assignee_id: int = 1788822,
    priority: str = "P2",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a task in Freedcamp.
    Uses multipart/form-data with a 'data' field containing the JSON payload.
    Returns a dictionary with {success, task_id, task_url, response|error}.
    """
    if not all([API_KEY, API_SECRET, PROJECT_ID, TASKGROUP_ID]):
        logger.error("Missing Freedcamp API credentials or project/task group IDs in .env.")
        return {"success": False, "error": "Missing API credentials or project/task group IDs"}

    payload_dict = {
        "project_id": PROJECT_ID,
        "task_group_id": TASKGROUP_ID,
        "title": title,
        "description": description,
        "assigned_to_id": 1788822,
        "priority": 3, # Default to 2 (P1 equivalent in map) if priority string is invalid
    }
    if due_date:  # Expected format YYYY-MM-DD
        payload_dict["due_date"] = due_date

    logger.debug(f"[FC-REQ] Payload for Freedcamp: {json.dumps(payload_dict, indent=2)}")

    try:
        auth_params = _auth() # Can raise ValueError if keys are missing
        
        # Freedcamp API expects the JSON payload as a string in a 'data' form field.
        # Using 'files' parameter with None for filename sends multipart/form-data.
        form_data_payload = {'data': (None, json.dumps(payload_dict))}
        
        res = requests.post(
            f"{BASE_URL}/tasks",
            params=auth_params,
            files=form_data_payload,
            verify=False  # <<< PRIVREMENO ZA TESTIRANJE SSL PROBLEMA
        )
        res.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
        
        response_json = res.json()
        # Successful task creation usually has the task details under a "data" key in Freedcamp's response
        task_data = response_json.get("data", {}) 
        task_id = task_data.get("id")
        task_url = task_data.get("url")  # API returns full or relative link

        # prepend host if link is relative
        if task_url and task_url.startswith("/"):
            task_url = f"https://freedcamp.com{task_url}"

        if task_id and task_url:
            logger.info(f"Successfully created Freedcamp task {task_id}. URL: {task_url}")
            return {
                "success": True,
                "task_id": task_id,
                "task_url": task_url,
                "response": task_data,
            }
        else:
            # Freedcamp's API might return 200 OK but with an error object in JSON if something went wrong with the data itself
            # Or if 'id' is missing, it's an issue.
            internal_error_msg = response_json.get("error", {}).get("message", "No task ID in response and no specific error message.")
            logger.error(f"Freedcamp task creation API call successful (HTTP {res.status_code}) but no 'id' found in response 'data' field or error reported. Response: {res.text}. Internal error: {internal_error_msg}")
            return {"success": False, "error": f"Task creation reported success by API (HTTP {res.status_code}) but task details/ID are missing. Freedcamp msg: {internal_error_msg}", "response": response_json}

    except requests.exceptions.HTTPError as http_err:
        error_text = http_err.response.text if http_err.response else "No response body"
        status_code = http_err.response.status_code if http_err.response else "N/A"
        logger.error(f"Freedcamp API HTTP error: {http_err}. Status: {status_code}. Response: {error_text}")
        # Attempt to parse JSON from error response, as Freedcamp often returns JSON errors
        try:
            error_response_json = http_err.response.json()
            error_detail = error_response_json.get("error", {}).get("message", error_text)
        except json.JSONDecodeError:
            error_detail = error_text
        return {"success": False, "error": str(http_err), "response_detail": error_detail, "status_code": status_code}
    except ValueError as ve: # Catch ValueError from _auth
        logger.error(f"ValueError during Freedcamp task creation (likely API key issue): {ve}")
        return {"success": False, "error": str(ve)}
    except Exception as e:
        logger.exception("An unexpected error occurred while creating Freedcamp task.") # Logs full stack trace
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"} 