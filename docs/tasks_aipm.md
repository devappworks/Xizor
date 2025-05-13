# tasks_aipm.md
*AI PM Task-Creator — Sprint Board*  
*(Agents SDK edition — generated 2025-05-09)*
.
---

## Legend

| Symbol | Meaning |
|--------|---------|
| ◻️ | To-Do |
| ⬜️ | In Progress |
| ✅ | Done |

Replace **◻️** with **✅** as you complete tasks.

---

## Sprint 0 — Environment & Repo Bootstrap  *(½ week)*

| ID | Task | Ref | Status |
|----|------|-----|--------|
| 0.1 | Set up Python 3.11 venv & `pip install openai-agents slack_sdk gspread` | — | ◻️ |
| 0.2 | Create private GitHub repo `ai-pm-agent` with MIT license | Git | ◻️ |
| 0.3 | Add `.gitignore`, `.env.example`, pre-commit hooks | Housekeeping | ◻️ |
| 0.4 | Commit **agent_sdk_full_reference.md** & **ai_pm_agent_plan.md** under `/docs` | — | ◻️ |

---

## Sprint 1 — Slack Listener MVP  *(1 week)*

| ID | Task | SDK / API | Status |
|----|------|-----------|--------|
| 1.1 | Create Slack app, enable `chat:write,im:history` scopes | Slack API | ◻️ |
| 1.2 | Implement `slack_events.py` Flask (or FastAPI) endpoint | — | ◻️ |
| 1.3 | Echo incoming DM text back to sender | Slack SDK | ◻️ |
| 1.4 | Unit test: DM “ping” → expect “pong” | Pytest | ◻️ |
| 1.5 | Enable `OPENAI_TRACE=1` and verify output | Agents SDK | ◻️ |

---

## Sprint 2 — TaskDraftAgent  *(1 week)*

| ID | Task | SDK ref | Status |
|----|------|---------|--------|
| 2.1 | Define `Task` Pydantic model (plan § 3) | Pydantic | ◻️ |
| 2.2 | Prompt engineer LLM to map summary → Task JSON | Agents SDK | ◻️ |
| 2.3 | Guardrail: fail if any mandatory field empty | Guardrails | ◻️ |
| 2.4 | Unit test fixtures (happy & edge cases) | Pytest | ◻️ |
| 2.5 | Trace JSON output in console | — | ◻️ |

---

## Sprint 3 — SheetWriterAgent  *(1 week)*

| ID | Task | API | Status |
|----|------|-----|--------|
| 3.1 | Set up Google Service Account creds JSON | GCP | ◻️ |
| 3.2 | Build `@tool def append_to_sheet(task:Task)->int` | gspread | ◻️ |
| 3.3 | Implement SheetWriterAgent that calls the tool | Agents SDK | ◻️ |
| 3.4 | Retry logic: exponential back-off on 5xx | — | ◻️ |
| 3.5 | Integration test TaskDraft→SheetWriter | — | ◻️ |

---

## Sprint 4 — NotifierAgent  *(1 week)*

| ID | Task | API | Status |
|----|------|-----|--------|
| 4.1 | Build `@tool def slack_dm(user:str,msg:str)->dict` | Slack SDK | ◻️ |
| 4.2 | Implement NotifierAgent (task link + JSON) | Agents SDK | ◻️ |
| 4.3 | Rate-limit guardrail (≤1 msg/s) | Guardrails | ◻️ |
| 4.4 | Integration test SheetWriter→Notifier | — | ◻️ |

---

## Sprint 5 — Orchestrator & End-to-End Runner  *(1 week)*

| ID | Task | SDK ref | Status |
|----|------|---------|--------|
| 5.1 | Create OrchestratorAgent to chain B→C→D | § 2 | ◻️ |
| 5.2 | Implement `Runner` invoked from Slack event | Agents SDK | ◻️ |
| 5.3 | Happy-path smoke test (summary → DM) | Pytest | ◻️ |
| 5.4 | Log hand-off trace JSON to `/logs` | Tracing | ◻️ |

---

## Sprint 6 — CI/CD & Observability  *(1 week)*

| ID | Task | Tool | Status |
|----|------|------|--------|
| 6.1 | Dockerfile & `docker-compose.yml` | DevOps | ◻️ |
| 6.2 | GitHub Actions: lint, tests, build image | CI | ◻️ |
| 6.3 | Deploy to Railway (free tier) | Infra | ◻️ |
| 6.4 | Optional: send traces to Langfuse | Observability | ◻️ |

---

## Sprint 7 — Hardening & Docs  *(1 week)*

| ID | Task | Ref | Status |
|----|------|-----|--------|
| 7.1 | Security sweep (secrets in Doppler) | DevOps | ◻️ |
| 7.2 | Add graceful Slack error handling | Slack SDK | ◻️ |
| 7.3 | Write `README.md` + architecture diagram | Docs | ◻️ |
| 7.4 | Stakeholder demo & feedback loop | — | ◻️ |

---

### Backlog / Stretch

| Idea | Notes |
|------|-------|
| Auto-priority via sentiment classification | Calls OpenAI sentiment endpoint |
| Due-date extraction from text (“next Friday”) | Use `dateparser` |
| Multi-task parsing from long summaries | Loop over bullet list |

---

*End of file*
