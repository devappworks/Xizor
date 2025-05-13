"""
Central location for all Pydantic models used in the AI PM Agent app.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class Task(BaseModel):
    title: str
    description: str
    assignee: str  # Slack @handle or email
    due_date: Optional[str]  # ISO date string
    priority: Literal["P0", "P1", "P2"]
    source_channel: str  # Slack channel id

class FreedcampInfo(BaseModel):
    success: bool
    task_id: Optional[str] = None
    task_url: Optional[str] = None
    error: Optional[str] = None

    # Removed the custom get_schema method to rely on Pydantic's default schema generation
    # @classmethod
    # def get_schema(cls) -> dict:
    #     return {
    #         "type": "object",
    #         "properties": {
    #             "title": {"type": "string"},
    #             "description": {"type": "string"},
    #             "assignee": {"type": "string"},
    #             "due_date": {"type": ["string", "null"]},
    #             "priority": {"type": "string", "enum": ["P0", "P1", "P2"]},
    #             "source_channel": {"type": "string"}
    #         },
    #         "required": ["title", "description", "assignee", "priority", "source_channel"],
    #         # "additionalProperties": False # Attempted fix, but removing get_schema entirely now
    #     } 