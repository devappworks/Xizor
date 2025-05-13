from agents import Agent, Runner
from pm_agents.task_draft_agent import TaskDraftAgent, TaskDraftOutput, Task
from tools.freedcamp_api import create_freedcamp_task # Correct non-src path
from models import FreedcampInfo
from pydantic import BaseModel
from typing import Literal, Optional
import logging
from pm_agents.user_map import SLACK_TO_FC # Correct non-src path

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
            tools=[], # Changed: create_freedcamp_task removed as per Prompt2.md
            output_type=OrchestratorResponse
        )

    async def run(self, user_input: str, context) -> OrchestratorResponse:
        logger.info("OrchestratorAgent.run invoked")
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

        assignee_fc_id = SLACK_TO_FC.get(task_details.assignee.lower(), 0) if task_details.assignee else 0
        logger.info(f"Mapped Slack assignee '{task_details.assignee}' to Freedcamp ID: {assignee_fc_id}")

        try:
            logger.info(f"Creating task in Freedcamp: {task_details.title}")
            fc_result = create_freedcamp_task( # Direct call
                title=task_details.title,
                description=task_details.description,
                assignee_id=assignee_fc_id,
                priority=task_details.priority,
                due_date=task_details.due_date
            )
           
            logger.info(f"Freedcamp API direct call response: {fc_result}")
            
            url_from_dict = fc_result.get("task_url")
            logger.info(f"[DEBUG Orchestrator] Task URL from fc_result dict: {url_from_dict}")

            if fc_result.get("success"):
                freedcamp_info = FreedcampInfo(**fc_result)
            else:
                freedcamp_info = FreedcampInfo(
                    success=False,
                    error=fc_result.get("error", "Unknown error from Freedcamp API call"),
                    task_id=None, task_url=None, response=fc_result.get("response")
                )

            if freedcamp_info.success and freedcamp_info.task_id:
                success_message = (
                    f"Task created successfully in Freedcamp (ID: {freedcamp_info.task_id}):\n\n"
                    f"*Title:* {task_details.title}\n"
                    f"*Description:* {task_details.description}\n"
                    f"*Assignee:* {task_details.assignee} (Freedcamp ID: {assignee_fc_id})\n"
                    f"*Priority:* {task_details.priority}\n"
                    f"*Due Date:* {task_details.due_date or 'Not specified'}\n\n"
                    f"*Freedcamp Link:* {freedcamp_info.task_url}"
                )
                return OrchestratorResponse(
                    status="success", message=success_message,
                    task=task_details, freedcamp_info=freedcamp_info
                )
            else:
                error_message = freedcamp_info.error or fc_result.get("error", "Unknown error creating task in Freedcamp")
                logger.error(f"Freedcamp task creation failed: {error_message}. API Response: {fc_result}")
                return OrchestratorResponse(
                    status="error", message=f"Task drafted but failed to create in Freedcamp: {error_message}",
                    task=task_details, freedcamp_info=freedcamp_info
                )
        except Exception as e:
            logger.error(f"Exception during Freedcamp task creation process: {str(e)}", exc_info=True)
            return OrchestratorResponse(
                status="error", message=f"Internal error processing Freedcamp task creation: {str(e)}",
                task=task_details
            ) 