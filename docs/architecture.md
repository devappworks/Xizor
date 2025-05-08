# System Architecture

## High-Level Data Flow

```plaintext
┌──────────────┐ 1  ┌───────────────┐ 2  ┌─────────┐ 3  ┌────────────┐ 4  ┌──────────────┐
│ Internal AI  ├───▶│ Slack Bot /   ├───▶│  LLM    ├───▶│ Freedcamp  ├───▶│ Slack Notif  │
│ Recorder     │    │  Event Hub    │    │ Extract │    │  REST API │    │  (channels)  │
└──────────────┘    └───────────────┘    └─────────┘    └────────────┘    └──────────────┘
        ▲                                                        │
        │                                                        ▼
        └──────────────────────  5. Firestore audit  ─────────────────────┘
```

## Core Modules

### 1. Slack Ingest (`slack_ingest.py`)
- Handles incoming Slack events
- Validates Slack signatures
- Extracts transcript content
- Forwards to processing pipeline

### 2. Task Extractor (`task_extractor.py`)
- Processes raw transcript text
- Calls OpenAI API for task extraction
- Formats extracted tasks
- Handles retry logic for API calls

### 3. FreedCamp Client (`freedcamp_client.py`)
- Manages FreedCamp API communication
- Creates tasks with proper formatting
- Handles API authentication
- Implements error handling and retries

### 4. Slack Notifier (`slack_notify.py`)
- Formats task summaries
- Creates rich Slack messages
- Handles message posting
- Manages error notifications

### 5. Audit Logger (`audit_log.py`)
- Records all system events
- Maintains audit trail in Firestore
- Handles structured logging
- Supports debugging and analytics

## Data Models and Contracts

### Module Interfaces

| Module          | Input                | Output               |
|-----------------|----------------------|----------------------|
| slack_ingest    | SlackEvent          | Transcript          |
| task_extractor  | Transcript          | List[Task]          |
| freedcamp_client| List[Task]          | List[FCResponse]    |
| slack_notify    | List[FCResponse]    | None                |
| audit_log       | Any                 | Firestore Write     |

### Key Data Structures

```python
class Transcript(BaseModel):
    text: str
    meeting_id: str
    channel_id: str
    timestamp: datetime

class Task(BaseModel):
    title: str
    assignee_email: EmailStr | None
    due_date: datetime | None
    description: str | None

class FCResponse(BaseModel):
    task_id: int
    url: str
    status: str
```

## Security Architecture

### Authentication
- Slack Bot Token validation
- OpenAI API key management
- FreedCamp API token handling
- Firebase service account auth

### Data Protection
- Environment variable encryption
- Secure token storage
- Input sanitization
- Output validation

## Monitoring and Logging

### Metrics Collection
- API response times
- Task extraction success rate
- Error rates by module
- System latency

### Audit Trail
- All operations logged to Firestore
- Structured event logging
- Debug information preservation
- Analytics support 