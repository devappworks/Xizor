# tests/test_freedcamp.py
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
load_dotenv() 

# Assuming 'src' directory is in PYTHONPATH or tests are run from the project root
# allowing for `from src.tools...`
# Update import to reflect non-src structure
from tools.freedcamp_api import create_freedcamp_task

def test_fc_smoke():
    """
    Smoke test for the Freedcamp task creation function.
    Requires Freedcamp API credentials (API_KEY, API_SECRET) and IDs 
    (PROJECT_ID, TASK_GROUP_ID) to be set in the .env file.
    """
    print("\nRunning Freedcamp Smoke Test...")
    # Check if necessary environment variables are loaded
    api_key_loaded = bool(os.getenv("FREEDCAMP_API_KEY"))
    project_id_loaded = bool(os.getenv("FREEDCAMP_PROJECT_ID"))
    task_group_id_loaded = bool(os.getenv("FREEDCAMP_TASK_GROUP_ID"))

    print(f"  FREEDCAMP_API_KEY loaded: {api_key_loaded}")
    print(f"  FREEDCAMP_PROJECT_ID loaded: {project_id_loaded}")
    print(f"  FREEDCAMP_TASK_GROUP_ID loaded: {task_group_id_loaded}")

    if not all([api_key_loaded, project_id_loaded, task_group_id_loaded]):
        print("  Skipping test: Not all required Freedcamp environment variables are set.")
        # Or raise an error/skip using pytest.skip if in a pytest environment
        # For now, just assert False with a clear message.
        assert False, "Missing required Freedcamp .env variables for testing."
        return

    print("  Attempting to create Freedcamp task...")
    result = create_freedcamp_task(
        title="Cursor Smoke Test Task (via Pytest)",
        description="This is a test task created by an automated smoke test.",
        assignee_id=0,  # 0 means unassigned
        priority="P1",  # Corresponds to 2 in PRIO_MAP {"P0":3,"P1":2,"P2":1}
        due_date="2025-12-31" # Example due date
    )
    
    print(f"  Freedcamp API call result:\n{json.dumps(result, indent=2)}")
    
    assert result.get("success") is True, f"API call failed: {result.get('error', 'Unknown error')}. Full response: {result.get('response')}"
    assert result.get("task_id") is not None, "Task ID not found in successful response."
    assert result.get("task_url") is not None, "Task URL not found in successful response."
    
    print(f"  Test task created successfully in Freedcamp!")
    print(f"    Task ID: {result['task_id']}")
    print(f"    Task URL: {result['task_url']}\n") 