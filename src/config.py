"""
Configuration settings for the AgenticPM application.
"""
from typing import Dict, Any

# Slack Configuration
SLACK_CONFIG: Dict[str, Any] = {
    "DEFAULT_CHANNEL_ID": "D08R4VD5D3L",  # Default channel for sending messages
    "BOT_SCOPES": [
        "channels:history",
        "chat:write",
        "chat:write.public"
    ]
}

# Application Settings
APP_NAME = "AgenticPM"
APP_VERSION = "0.1.0" 