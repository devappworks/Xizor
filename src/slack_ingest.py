"""
Slack Ingest Module - Handles incoming Slack events and messages.
"""
import json
import os
import time
from typing import Dict, Any, List, Union, Set
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SlackIngestHandler:
    def __init__(self, bot_token: str, signing_secret: str):
        """Initialize the Slack event handler.
        
        Args:
            bot_token (str): Slack bot user OAuth token
            signing_secret (str): Slack signing secret for request verification
        """
        self.client = WebClient(token=bot_token)
        self.signature_verifier = SignatureVerifier(signing_secret=signing_secret)
        self.processed_messages: Set[str] = set()  # Store message IDs we've processed
        self.last_message_time = 0  # Store last message timestamp
        
        # Get bot's own ID to prevent self-replies
        try:
            auth_response = self.client.auth_test()
            self.bot_user_id = auth_response["user_id"]
            # Also get the bot's app ID
            self.bot_app_id = auth_response.get("app_id")
        except SlackApiError as e:
            print(f"Error getting bot user ID: {e}")
            self.bot_user_id = None
            self.bot_app_id = None
        
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
            
            # Get event ID and timestamp
            event_id = body.get("event_id", "")
            event_time = body.get("event_time", 0)
            
            # Check if we've already processed this event
            if event_id in self.processed_messages:
                print(f"Skipping already processed event: {event_id}")
                return {"ok": True}
                
            # Check for minimum time between messages (1 second)
            current_time = time.time()
            if current_time - self.last_message_time < 1:
                print("Rate limiting: Message received too quickly after last one")
                return {"ok": True}
            
            # Handle direct messages with additional checks
            if (event["type"] == "message" and 
                "channel_type" in event and
                event["channel_type"] == "im" and
                "subtype" not in event and  # Ignore message subtypes (like message_changed)
                "bot_id" not in event and   # Ignore bot messages
                "app_id" not in event and   # Ignore app messages
                event.get("user") != self.bot_user_id and  # Ignore self messages
                not self._is_bot_mention(event.get("text", ""))):  # Ignore messages mentioning the bot
                    
                    # Store event ID and update last message time
                    self.processed_messages.add(event_id)
                    self.last_message_time = current_time
                    
                    # Process the message
                    await self.handle_direct_message(event)
                    
                    # Cleanup old message IDs (keep last 1000)
                    if len(self.processed_messages) > 1000:
                        self.processed_messages = set(list(self.processed_messages)[-1000:])
                    
        return {"ok": True}
        
    def _is_bot_mention(self, text: str) -> bool:
        """Check if the message mentions the bot.
        
        Args:
            text (str): Message text to check
            
        Returns:
            bool: True if the message mentions the bot, False otherwise
        """
        if not text:
            return False
            
        # Check for bot user ID mention
        if self.bot_user_id and f"<@{self.bot_user_id}>" in text:
            return True
            
        # Check for bot app ID mention
        if self.bot_app_id and f"<@{self.bot_app_id}>" in text:
            return True
            
        return False
        
    async def handle_direct_message(self, event: Dict[str, Any]) -> None:
        """Handle direct messages sent to the bot.
        
        Args:
            event (Dict[str, Any]): The message event from Slack
        """
        try:
            # Extract message text and channel
            message_text = event.get("text", "")
            channel_id = event["channel"]
            
            # Ignore empty messages
            if not message_text.strip():
                return
                
            # Process the message to extract tasks
            result = await self.process_message(message_text)
            
            # Format and send response based on whether it's an error or tasks
            if isinstance(result, str):  # Error message
                response = f"❌ *Error:* {result}"
            else:  # List of tasks
                response = self.format_task_response(result)
            
            self.client.chat_postMessage(
                channel=channel_id,
                text=response,
                thread_ts=event.get("thread_ts")  # Reply in thread if message is in thread
            )
            
        except SlackApiError as e:
            print(f"Error handling direct message: {e}")
            
    async def process_message(self, message: str) -> Union[List[Dict[str, Any]], str]:
        """Process a message to extract tasks using OpenAI.
        
        Args:
            message (str): The message to process
            
        Returns:
            Union[List[Dict[str, Any]], str]: List of extracted tasks or error message
        """
        try:
            # Create system instructions
            system_message = """You are a professional project manager with 10 years of experience. 
            Extract tasks from messages and format them as structured data.
            Return ONLY a valid JSON array of tasks with no additional text.
            For each task include:
            - name (required)
            - description (required)
            - assignee (if mentioned)
            - priority (High/Medium/Low)
            - subtasks (if any)
            
            Example format:
            [
                {
                    "name": "Task name",
                    "description": "Task description",
                    "assignee": "person@example.com",
                    "priority": "High",
                    "subtasks": [
                        {
                            "name": "Subtask 1"
                        }
                    ]
                }
            ]"""

            # Call OpenAI API using chat completions
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.1  # Low temperature for more consistent output
            )

            # Parse the response
            try:
                content = response.choices[0].message.content
                tasks = json.loads(content)
                # If the response is a list, return it directly
                # If it's a dict with a 'tasks' key, return the tasks array
                return tasks if isinstance(tasks, list) else tasks.get('tasks', [])
            except (json.JSONDecodeError, AttributeError, IndexError) as e:
                print(f"Error parsing OpenAI response: {e}")
                return "Sorry, I couldn't process your request at the moment. Please try again."

        except Exception as e:
            # Log the actual error for debugging
            print(f"Error processing message with OpenAI: {e}")
            # Return user-friendly message
            return "Sorry, I couldn't process your request at the moment. Please try again."
        
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