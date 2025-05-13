import os
import requests
import logging
import json
from dotenv import load_dotenv
from agents import function_tool
from datetime import datetime
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Freedcamp API credentials
FREEDCAMP_API_KEY = os.getenv("FREEDCAMP_API_KEY")
FREEDCAMP_API_SECRET = os.getenv("FREEDCAMP_API_SECRET")
FREEDCAMP_PROJECT_ID = os.getenv("FREEDCAMP_PROJECT_ID")

BASE_URL = "https://freedcamp.com/api/v1"

def _get_auth_params():
    """Return the authentication parameters for Freedcamp API calls."""
    return {
        "api_key": FREEDCAMP_API_KEY,
        "api_secret": FREEDCAMP_API_SECRET,
    }

def _convert_priority(internal_priority: str) -> int:
    """Convert internal priority format (P0, P1, P2) to Freedcamp priority (1-3)."""
    priority_map = {
        "P0": 1,  # High priority in Freedcamp
        "P1": 2,  # Medium priority in Freedcamp
        "P2": 3,  # Low priority in Freedcamp
    }
    return priority_map.get(internal_priority, 2)  # Default to medium if not recognized

def _format_due_date(due_date: Optional[str]) -> Optional[str]:
    """Format the due date for Freedcamp API (YYYY-MM-DD)."""
    if not due_date:
        return None
    
    # If already in YYYY-MM-DD format, return as is
    if len(due_date) == 10 and due_date[4] == '-' and due_date[7] == '-':
        return due_date
    
    # Otherwise try to parse and format
    try:
        # Try various formats
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y'):
            try:
                date_obj = datetime.strptime(due_date, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If we couldn't parse, log warning and return None
        logger.warning(f"Could not parse due date: {due_date}")
        return None
    except Exception as e:
        logger.error(f"Error formatting due date: {e}")
        return None

@function_tool
def create_freedcamp_task(title: str, description: str, assignee: str, 
                        priority: str, due_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new task in Freedcamp.
    
    Args:
        title: Task title
        description: Task description
        assignee: Name of the assignee (will be used as is)
        priority: Priority level (P0, P1, P2)
        due_date: Optional due date in YYYY-MM-DD format
        
    Returns:
        Dict containing the response from Freedcamp API
    """
    logger.info(f"Creating Freedcamp task: {title}")
    
    # Check if API credentials are set
    if not FREEDCAMP_API_KEY or not FREEDCAMP_API_SECRET or not FREEDCAMP_PROJECT_ID:
        error_msg = "Freedcamp API credentials or project ID not set"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Prepare API endpoint and params
    endpoint = f"{BASE_URL}/projects/{FREEDCAMP_PROJECT_ID}/tasks"
    params = _get_auth_params()
    
    # Convert the priority
    fc_priority = _convert_priority(priority)
    
    # Format the due date
    formatted_due_date = _format_due_date(due_date)
    
    # Prepare the payload
    payload = {
        "project_id": FREEDCAMP_PROJECT_ID,
        "title": title,
        "description": description,
        "priority": fc_priority,
        "assignee": assignee,  # Note: This might need adjustment based on how Freedcamp handles assignees
    }
    
    # Add due date if provided
    if formatted_due_date:
        payload["due_date"] = formatted_due_date
    
    try:
        # Make the API request
        response = requests.post(endpoint, params=params, json=payload)
        response.raise_for_status()  # Raise exception for non-2xx responses
        
        data = response.json()
        logger.debug("[FC-RAW]\n" + json.dumps(data, indent=2))
        
        task_id = data.get('id')
        logger.info(f"Task created successfully in Freedcamp. Task ID: {task_id}")
        
        # Since we're using /projects/{project_id}/tasks endpoint, we know the project_id
        project_id = FREEDCAMP_PROJECT_ID
        
        logger.debug(f"[DEBUG] project_id: {project_id}")
        
        task_url = f"https://freedcamp.com/view/{project_id}/tasks/{task_id}"
        logger.debug(f"[DEBUG] task_url : {task_url}")
        
        return {
            "success": True,
            "task_id": task_id,
            "task_url": task_url,
            "response": data
        }
    
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err}"
        logger.error(error_msg)
        try:
            response_data = response.json()
            logger.error(f"API response: {response_data}")
            return {"success": False, "error": error_msg, "response": response_data}
        except:
            return {"success": False, "error": error_msg, "status_code": response.status_code}
    
    except Exception as err:
        error_msg = f"Error creating task in Freedcamp: {err}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg} 