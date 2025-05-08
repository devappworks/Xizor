"""
Main application module - Handles HTTP server and routes.
"""
import os
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from slack_ingest import SlackIngestHandler
from slack_sender import SlackSender
from config import SLACK_CONFIG

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AgenticPM")

# Get the default token
DEFAULT_SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not DEFAULT_SLACK_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable is not set")

# Initialize default Slack handlers
slack_event_handler = SlackIngestHandler(
    bot_token=DEFAULT_SLACK_TOKEN,
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

class Task(BaseModel):
    """Model for a task"""
    name: str
    description: str
    assignee: Optional[str] = None
    priority: str = "Medium"
    subtasks: Optional[List[dict]] = None

    """Model for processing message requests"""
    text: str
    response_channel: Optional[str] = SLACK_CONFIG["DEFAULT_CHANNEL_ID"]

class MessageRequest(BaseModel):
    """Model for simple message requests"""
    channel_id: str = SLACK_CONFIG["DEFAULT_CHANNEL_ID"]
    message: str

    """Model for incoming transcript requests"""
    channel_id: str = SLACK_CONFIG["DEFAULT_CHANNEL_ID"]
    text: str
    thread_ts: Optional[str] = None

@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle incoming Slack events.
    
    Args:
        request (Request): The incoming HTTP request
        
    Returns:
        dict: Response to send back to Slack
    """
    try:
        # Get request headers and body
        headers = dict(request.headers)
        body = await request.json()
        
        # Handle the webhook
        response = await slack_event_handler.handle_webhook(headers, body)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-message")
def send_message(
    request: MessageRequest,
    authorization: Optional[str] = Header(None)
):
    """Send a simple message to a Slack channel.
    
    Args:
        request (MessageRequest): The message request containing channel_id and message
        authorization (Optional[str]): The Authorization header
        
    Returns:
        dict: Response indicating success or failure
    """
    try:
        # Use token from Authorization header if provided, otherwise use default token
        token = DEFAULT_SLACK_TOKEN
        if authorization and authorization.startswith('Bearer '):
            token = authorization.split(' ')[1]
        
        if not token:
            raise HTTPException(status_code=401, detail="No valid token provided")
            
        # Create a new SlackSender instance with the token
        sender = SlackSender(bot_token=token)
        
        # Send the message
        response = sender.send_message(
            channel_id=request.channel_id,
            message=request.message
        )
        
        if response["status"] == "success":
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail=response["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 