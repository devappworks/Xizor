# AI PM Agent

A Slack-native AI Project Manager that turns meeting summaries into structured tasks, logs them to Google Sheets, and notifies assignees.

## Environment Setup

1. **Python Version**
   - Use Python 3.11

2. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-pm-agent
   ```

3. **Create a virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env` and fill in your secrets:
     - `OPENAI_API_KEY`
     - `SLACK_BOT_TOKEN`
     - `SLACK_SIGNING_SECRET`
     - `GOOGLE_SERVICE_JSON`
     - `SHEET_ID`

6. **Run the app**
   - (Instructions for running will be added as the app is built)

---

See `/docs/ai_pm_agent_plan.md` for architecture and roadmap. 