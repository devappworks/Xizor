import os
import logging
from fastapi import FastAPI, Request, Header, Response
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv
import json
from dataclasses import dataclass

from agents import Runner
from pm_agents import OrchestratorAgent
from pm_agents.orchestrator_agent import OrchestratorResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

slack_token = os.getenv("SLACK_BOT_TOKEN")
signing_secret = os.getenv("SLACK_SIGNING_SECRET")
client = WebClient(token=slack_token)
verifier = SignatureVerifier(signing_secret)

@dataclass
class SlackContext:
    channel: str
    user: str

@app.post("/slack/events")
async def slack_events(
    request: Request,
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None)
):
    body = await request.body()
    if not verifier.is_valid_request(body, {
        "X-Slack-Signature": x_slack_signature,
        "X-Slack-Request-Timestamp": x_slack_request_timestamp
    }):
        return Response(content="Invalid request", status_code=403)

    data = await request.json()

    # Slack URL verification challenge
    if data.get("type") == "url_verification":
        return Response(content=data.get("challenge"), media_type="text/plain")

    # Handle message events
    if "event" in data:
        event = data["event"]
        if (
            event.get("type") == "message"
            and event.get("channel_type") == "im"
            and "bot_id" not in event
        ):
            user = event["user"]
            text = event["text"]
            channel = event["channel"]

            # Create context with Slack information
            context = SlackContext(channel=channel, user=user)

            # Send initial acknowledgment
            client.chat_postMessage(
                channel=channel, 
                text="Processing your request... :hourglass_flowing_sand:"
            )

            try:
                # Run the OrchestratorAgent to process the task with context
                #logger.info("Running OrchestratorAgent...")
                run_result = await Runner.run(OrchestratorAgent(), text, context=context)
                #logger.info(f"OrchestratorAgent result: {run_result.final_output}")
                
                # Try to validate the response
                try:
                    result = OrchestratorResponse.model_validate(run_result.final_output)
                    #logger.info(f"Validated response: {result}")
                except Exception as validation_error:
                    logger.error(f"Validation error: {validation_error}")
                    logger.error(f"Invalid response structure: {run_result.final_output}")
                    raise validation_error
                
                # Format the response message based on status
                if result.status == "success" and result.task:
                    # Get Freedcamp info if available
                    freedcamp_info = result.freedcamp_info
                    if freedcamp_info:
                        freedcamp_task_id = freedcamp_info.task_id or "N/A"
                        freedcamp_task_url = freedcamp_info.task_url or ""
                        emoji = ":clipboard:" if freedcamp_info.success else ":warning:"
                    else:
                        freedcamp_task_id = "N/A"
                        freedcamp_task_url = ""
                        emoji = ":warning:"
                    
                    # Create task details message
                    task = result.task
                    
                    # Create detailed message
                    detailed_message = (
                        f"{emoji} *Task Details*\n\n"
                        f"*Title:* {task.title}\n"
                        f"*Description:* {task.description}\n"
                        f"*Assignee:* {task.assignee}\n"
                        f"*Priority:* {task.priority}\n"
                        f"*Due Date:* {task.due_date or 'Not specified'}"
                    )
                    
                    # Add Freedcamp information if available
                    if freedcamp_info and freedcamp_info.success:
                        detailed_message += (
                            f"\n\n*Freedcamp Information*\n"
                            f"*Task ID:* {freedcamp_task_id}\n"
                            f"*Task URL:* <{freedcamp_task_url}|Open in Freedcamp>"
                        )
                    
                    # Send the detailed task message
                    client.chat_postMessage(
                        channel=channel,
                        text=detailed_message,
                        parse="mrkdwn"  # Enable markdown formatting
                    )
                    
                    # Send a simple confirmation message for the operation result
                    if freedcamp_info and freedcamp_info.success:
                        confirmation = f":white_check_mark: Task '{task.title}' created successfully in Freedcamp!"
                    else:
                        confirmation = f":warning: Task created but Freedcamp integration failed: {freedcamp_info.error if freedcamp_info else 'Unknown error'}"
                    
                    client.chat_postMessage(
                        channel=channel,
                        text=confirmation
                    )
                else:
                    # Send error message
                    error_message = f":warning: {result.message}"
                    client.chat_postMessage(channel=channel, text=error_message)
            except Exception as e:
                # Handle any errors
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
                error_msg = f":x: An error occurred: {str(e)}"
                client.chat_postMessage(channel=channel, text=error_msg)

    return Response(content="", status_code=200)

# To run: uvicorn src.slack_events:app --reload --port 8080 