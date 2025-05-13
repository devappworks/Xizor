import os
import gspread
from models import Task

# This function will be registered as a tool for the SheetWriterAgent

def append_to_sheet(task: Task) -> int:
    """Append a Task to the Google Sheet and return the created row number."""
    # Load credentials and sheet ID from environment
    creds_path = os.getenv("GOOGLE_SERVICE_JSON")
    sheet_id = os.getenv("1FM74Bl-44_TSa6YrcpMFYyMbCFvlpTfHPD49PgVor7w")
    if not creds_path or not sheet_id:
        raise RuntimeError("Missing Google Sheets credentials or sheet ID.")
    # Authenticate and open the sheet
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1  # or use a specific worksheet name
    # Prepare row data in schema order
    row = [
        task.title,
        task.description,
        task.assignee,
        task.due_date or '',
        task.priority,
        task.source_channel,
        ''  # sheet_row will be filled after append
    ]
    inserted = worksheet.append_row(row, value_input_option="USER_ENTERED")
    # Get the new row number (gspread returns None, so fetch row count)
    return len(worksheet.get_all_values()) 