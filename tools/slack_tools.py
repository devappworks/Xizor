import os
from slack_sdk import WebClient
from agents import function_tool

@function_tool
def slack_dm(user: str, msg: str) -> dict:
    """Send a Slack DM to the given user and return the API response as a dict."""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing SLACK_BOT_TOKEN.")
    
    client = WebClient(token=token)
    
    try:
        # Send the message
        response = client.chat_postMessage(
            channel=user,  # user ID or channel
            text=msg,
            parse="mrkdwn"  # Enable markdown formatting
        )
        return response.data
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "channel": user,
            "message": msg
        } 