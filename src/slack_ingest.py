"""
Slack Ingest Module - Handles incoming Slack events and messages.
"""
import json
import os
from typing import Dict, Any, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class SlackIngestHandler:
    def __init__(self, bot_token: str, signing_secret: str):
        """Initialize the Slack event handler.
        
        Args:
            bot_token (str): Slack bot user OAuth token
            signing_secret (str): Slack signing secret for request verification
        """
        self.client = WebClient(token=bot_token)
        self.signature_verifier = SignatureVerifier(signing_secret=signing_secret)
        
    async def handle_webhook(self, headers: Dict[str, str], body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming Slack webhook events.
        
        Args:
            headers (Dict[str, str]): Request headers
            body (Dict[str, Any]): Request body
            
        Returns:
            Dict[str, Any]: Response to send back to Slack
        """
        # Handle URL verification challenge
        if body.get("type") == "url_verification":
            return {"challenge": body["challenge"]}
            
        # Process events
        if "event" in body:
            event = body["event"]
            
            # Handle direct messages
            if event["type"] == "message" and "channel_type" in event:
                if event["channel_type"] == "im":  # Direct message
                    await self.handle_direct_message(event)
                    
        return {"ok": True}
        
    async def handle_direct_message(self, event: Dict[str, Any]) -> None:
        """Handle direct messages sent to the bot.
        
        Args:
            event (Dict[str, Any]): The message event from Slack
        """
        try:
            # Extract message text and channel
            message_text = event.get("text", "")
            channel_id = event["channel"]
            
            # Process the message to extract tasks
            tasks = await self.process_message(message_text)
            
            # Format and send response
            response = self.format_task_response(tasks)
            
            self.client.chat_postMessage(
                channel=channel_id,
                text=response,
                thread_ts=event.get("thread_ts")  # Reply in thread if message is in thread
            )
            
        except SlackApiError as e:
            print(f"Error handling direct message: {e}")
            
    async def process_message(self, message: str) -> List[Dict[str, Any]]:
        """Process a message to extract tasks using OpenAI.
        
        Args:
            message (str): The message to process
            
        Returns:
            List[Dict[str, Any]]: List of extracted tasks
        """
        try:
            # Create the prompt for OpenAI
            prompt = f"""Extract tasks from the following message. For each task, identify:
            - Name (required)
            - Description (required)
            - Assignee (if mentioned)
            - Priority (High/Medium/Low)
            - Subtasks (if any)

            Format the response as a JSON array of tasks.

            Message:
            {message}
            """

            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional project manager with 10 years of experience. Extract tasks from messages and format them as structured data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent output
                max_tokens=1000
            )

            # Parse the response
            try:
                tasks = json.loads(response.choices[0].message.content)
                return tasks
            except json.JSONDecodeError:
                print("Error parsing OpenAI response as JSON")
                return [{
                    "name": "Error Processing Task",
                    "description": "Could not parse the task information. Please try again.",
                    "priority": "Medium"
                }]

        except Exception as e:
            print(f"Error processing message with OpenAI: {e}")
            return [{
                "name": "Error Processing Task",
                "description": f"An error occurred while processing the task: {str(e)}",
                "priority": "Medium"
            }]
        
    def format_task_response(self, tasks: list) -> str:
        """Format tasks into a readable Slack message.
        
        Args:
            tasks (list): List of extracted tasks
            
        Returns:
            str: Formatted message
        """
        response = "📋 *Extracted Tasks:*\n\n"
        
        for task in tasks:
            response += f"*Task:* {task['name']}\n"
            response += f"*Description:* {task['description']}\n"
            if task.get('assignee'):
                response += f"*Assignee:* {task['assignee']}\n"
            response += f"*Priority:* {task['priority']}\n"
            
            if task.get('subtasks'):
                response += "*Subtasks:*\n"
                for subtask in task['subtasks']:
                    response += f"- {subtask.get('name', 'Unnamed subtask')}\n"
            
            response += "\n"
            
        return response 