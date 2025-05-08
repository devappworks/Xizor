# Technical Requirements

## Technology Stack
| Component    | Technology Choice                              | Justification                               |
|-------------|-----------------------------------------------|---------------------------------------------|
| Runtime     | Python 3.11 (Cloud Functions for Firebase)     | Cold-start-friendly, first-class GCP support|
| Hosting     | Firebase Functions + Firestore                 | Zero-ops, built-in auth & logging           |
| Messaging   | Slack Bot (Events API + Web API)              | Real-time ingestion & notifications         |
| LLM         | OpenAI gpt-4 (swap-able)                      | Best-in-class extraction                    |
| PM Tool     | FreedCamp REST v2                             | Company standard                            |
| Dev Tooling | Cursor (codegen) + Poetry (deps)              | Fast scaffolding & deterministic env        |

## Core Dependencies
```
slack_sdk
openai
httpx
google-cloud-firestore
python-dotenv
pydantic
pytest
```

## Module Structure
```
agentic_pm/
  ├─ src/
  │   ├─ slack_ingest.py
  │   ├─ task_extractor.py
  │   ├─ freedcamp_client.py
  │   ├─ slack_notify.py
  │   ├─ audit_log.py
  │   └─ main.py
  ├─ tests/
  ├─ .env.example
  ├─ pyproject.toml
  └─ README.md
```

## Data Models

### Task Schema
```python
class Task(BaseModel):
    title: str
    assignee_email: EmailStr | None
    due_date: datetime | None
    description: str | None
```

## API Requirements

### Environment Variables
```
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
OPENAI_API_KEY=
FREEDCAMP_API_TOKEN=
FREEDCAMP_PROJECT_ID=
FIRESTORE_PROJECT=
```

## Testing Requirements

| Layer           | Tool                         | Coverage                                   |
|----------------|------------------------------|---------------------------------------------|
| Pure Python    | pytest + pytest-asyncio      | Unit tests with LLM mocked                 |
| Firestore rules| firebase-emulator           | Read/write permissions                      |
| E2E            | pytest + ngrok CI tunnel     | Simulate Slack event → Slack notification  |

## Performance Requirements
- Cold start time: <300ms
- Task extraction accuracy: ≥95%
- Zero uncaught exceptions in production
- Automatic retries with back-off for API calls

## Security Requirements
- Secure storage of API keys and tokens
- Slack signature verification
- Firestore access control rules
- Input validation and sanitization 