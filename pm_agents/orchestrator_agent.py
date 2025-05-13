from agents import Agent, Runner
from pm_agents.task_draft_agent import TaskDraftAgent, TaskDraftOutput, Task
from tools.freedcamp_api import create_freedcamp_task
from models import FreedcampInfo
from pydantic import BaseModel
from typing import Literal, Optional
import logging

logger = logging.getLogger(__name__)

class OrchestratorResponse(BaseModel):
    status: Literal["success", "error"]
    message: str
    task: Optional[Task] = None
    freedcamp_info: Optional[FreedcampInfo] = None


class OrchestratorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            instructions="Drafts a task from user input, creates it in Freedcamp, and returns the full task object with detailed information.",
            tools=[create_freedcamp_task],
            output_type=OrchestratorResponse
        )

    async def run(self, user_input: str, context) -> OrchestratorResponse:
        logger.info("OrchestratorAgent.run invoked")
        # 1) Prosledi zadatak TaskDraftAgent-u
        td_run_result = await Runner.run(TaskDraftAgent, user_input, context=context)
        draft: TaskDraftOutput = td_run_result.final_output

        logger.info(f"TaskDraftAgent output: status='{draft.status}', message='{draft.message}', task_present={draft.task is not None}")

        if draft.status == "error":
            logger.info("TaskDraftAgent returned error, forwarding as OrchestratorResponse.")
            return OrchestratorResponse(status="error", message=draft.message, task=None)

        task_details: Task = draft.task
        if not task_details:
            logger.error("TaskDraftAgent status was success, but no task details provided.")
            return OrchestratorResponse(status="error", message="Task drafting succeeded but task details were missing.", task=None)

        #logger.info(f"Task details: title='{task_details.title}', assignee='{task_details.assignee}'")

        # Create the task in Freedcamp
        try:
            logger.info(f"Creating task in Freedcamp: {task_details.title}")
            fc_result = create_freedcamp_task(
                title=task_details.title,
                description=task_details.description,
                assignee=task_details.assignee,
                priority=task_details.priority,
                due_date=task_details.due_date
            )
            logger.info(f"Freedcamp API response: {fc_result}")
            # --- Explicit URL Log ---
            url_from_dict = fc_result.get("task_url")
            logger.info(f"[DEBUG] Task URL from fc_result dict: {url_from_dict}")
            # --- End Explicit URL Log ---
            freedcamp_info = FreedcampInfo(**fc_result)

            if freedcamp_info.success:
                # Task created successfully in Freedcamp
                freedcamp_task_id = freedcamp_info.task_id
                freedcamp_task_url = freedcamp_info.task_url
                
                # Create success message including Freedcamp information
                success_message = (
                    f"Task created successfully in Freedcamp (ID: {freedcamp_task_id}):\n\n"
                    f"*Title:* {task_details.title}\n"
                    f"*Description:* {task_details.description}\n"
                    f"*Assignee:* {task_details.assignee}\n"
                    f"*Priority:* {task_details.priority}\n"
                    f"*Due Date:* {task_details.due_date or 'Not specified'}\n\n"
                    f"*Freedcamp Link:* {freedcamp_task_url}"
                )
                
                return OrchestratorResponse(
                    status="success",
                    message=success_message,
                    task=task_details,
                    freedcamp_info=freedcamp_info
                )
            else:
                # Failed to create task in Freedcamp
                error_message = freedcamp_info.error or "Unknown error creating task in Freedcamp"
                logger.error(f"Freedcamp task creation failed: {error_message}")
                
                return OrchestratorResponse(
                    status="error",
                    message=f"Task drafted but failed to create in Freedcamp: {error_message}",
                    task=task_details,
                    freedcamp_info=freedcamp_info
                )
                
        except Exception as e:
            logger.error(f"Exception creating Freedcamp task: {str(e)}", exc_info=True)
            return OrchestratorResponse(
                status="error",
                message=f"Error creating task in Freedcamp: {str(e)}",
                task=task_details
            )

# Commenting out the old factory-based implementation
# ORCHESTRATOR_INSTRUCTIONS = """ ... """
# OrchestratorAgent_old_instance = Agent( ... ) 