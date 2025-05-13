import os
import asyncio
import logging
import json
from fastapi import FastAPI, Request, Header, Response
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web.async_client import AsyncWebClient
from dotenv import load_dotenv
from dataclasses import dataclass

from pm_agents.orchestrator_agent import OrchestratorAgent, OrchestratorResponse

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize Slack Async WebClient and signature verifier
client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))
verifier = SignatureVerifier(os.getenv("SLACK_SIGNING_SECRET"))

# In-memory set to dedupe Slack event IDs
processed_events = set()

@dataclass
class SlackContext:
    channel: str
    user:    str

async def handle_message(event: dict):
    """
    Background task to process a single Slack DM event.
    """
    channel = event["channel"]
    user    = event["user"]
    text    = event["text"]

    # Acknowledge processing
    await client.chat_postMessage(
        channel=channel,
        text="Processing your request... :hourglass_flowing_sand:"
    )

    # Run the OrchestratorAgent
    result: OrchestratorResponse = await OrchestratorAgent().run(text, SlackContext(channel, user))

    # Format and send response
    if result.status == "success" and result.task:
        task = result.task
        fci = result.freedcamp_info or type("o", (), {"success": False, "error": None, "task_id": None, "task_url": None})()
        emoji = ":clipboard:" if fci.success else ":warning:"

        detailed = (
            f"{emoji} *Task Details*\n\n"
            f"*Title:* {task.title}\n"
            f"*Description:* {task.description}\n"
            f"*Assignee:* {task.assignee}\n"
            f"*Priority:* {task.priority}\n"
            f"*Due Date:* {task.due_date or 'Not specified'}"
        )
        if fci.success:
            detailed += (
                f"\n\n*Freedcamp Information*\n"
                f"*Task ID:* {fci.task_id}\n"
                f"*Task URL:* <{fci.task_url}|Open in Freedcamp>"
            )
        await client.chat_postMessage(channel=channel, text=detailed, parse="mrkdwn")

        confirmation = (
            f":white_check_mark: Task '{task.title}' created successfully in Freedcamp!"
            if fci.success else f":warning: Task created but Freedcamp integration failed: {fci.error}"
        )
        await client.chat_postMessage(channel=channel, text=confirmation)
    else:
        # Error path
        await client.chat_postMessage(channel=channel, text=f":warning: {result.message}")

@app.post("/slack/events")
async def slack_events(
    request: Request,
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None)
):
    # Read and verify request body
    body = await request.body()
    if not verifier.is_valid_request(body, {
        "X-Slack-Signature": x_slack_signature,
        "X-Slack-Request-Timestamp": x_slack_request_timestamp
    }):
        return Response(content="Invalid request", status_code=403)

    data = json.loads(body)

    # URL verification challenge
    if data.get("type") == "url_verification":
        return Response(content=data.get("challenge"), media_type="text/plain")

    # Only handle event callbacks
    if data.get("type") != "event_callback":
        return Response(status_code=200)

    event = data.get("event", {})

    # Ignore edits, bot messages, and subtypes
    if event.get("subtype") or event.get("bot_id"):
        return Response(status_code=200)

    # Only direct IM messages
    if not (event.get("type") == "message" and event.get("channel_type") == "im"):
        return Response(status_code=200)

    # Deduplicate by event_id
    event_id = data.get("event_id")
    if event_id in processed_events:
        return Response(status_code=200)
    processed_events.add(event_id)

    # Acknowledge and process in background
    asyncio.create_task(handle_message(event))
    return Response(status_code=200)
