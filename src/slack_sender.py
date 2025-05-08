"""
Slack Sender Module - Handles sending messages to Slack channels.
"""
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackSender:
    def __init__(self, bot_token: str):
        """Initialize the Slack sender.
        
        Args:
            bot_token (str): Slack bot user OAuth token
        """
        self.client = WebClient(token=bot_token)

    def send_message(self, channel_id: str, message: str) -> Dict[str, Any]:
        """Send a simple message to a Slack channel.
        
        Args:
            channel_id (str): The ID of the channel to send the message to
            message (str): The message to send
            
        Returns:
            Dict[str, Any]: Response indicating success or failure
        """
        try:
            # Send the message using the WebClient
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            
            if response["ok"]:
                return {
                    "status": "success",
                    "message": "Message sent successfully",
                    "timestamp": response["ts"],
                    "channel": response["channel"]
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response.get('error', 'Unknown error')}"
                }

        except SlackApiError as e:
            error_message = f"The request to the Slack API failed. (url: {e.response.get('url', 'unknown')})\nThe server responded with: {e.response}"
            return {
                "status": "error",
                "message": error_message
            }