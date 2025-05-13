from agents import Agent, tool
from models import Task
from tools.gsheet_tools import append_to_sheet

SheetWriterAgent = Agent(
    name="SheetWriterAgent",
    instructions="Receive a Task and write it to Google Sheet via append_to_sheet.",
    tools=[append_to_sheet],
    output_type=int,
) 