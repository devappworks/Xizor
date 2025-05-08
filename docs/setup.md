# Setup Guide

## Prerequisites

1. Python 3.11 or higher
2. Poetry for dependency management
3. Firebase CLI
4. Node.js and npm (for Firebase emulators)
5. Git

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd agentic_pm
   ```

2. **Install Dependencies**
   ```bash
   poetry install
   ```

3. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Firebase Setup**
   ```bash
   firebase login
   firebase init
   firebase functions:config:set slack.token="YOUR_TOKEN"
   ```

## Configuration

### Required API Keys and Tokens

1. **Slack Configuration**
   - Create a Slack App in your workspace
   - Enable Events API
   - Add Bot Token Scopes:
     - `channels:history`
     - `chat:write`
     - `chat:write.public`

2. **OpenAI Setup**
   - Get API key from OpenAI dashboard
   - Set rate limits and budget

3. **FreedCamp Setup**
   - Generate API token
   - Note project ID
   - Configure webhook endpoints

4. **Firebase Setup**
   - Create new project
   - Enable Firestore
   - Download service account key

## Local Development

1. **Start Firebase Emulators**
   ```bash
   firebase emulators:start
   ```

2. **Run Development Server**
   ```bash
   poetry run python -m src.main --local
   ```

3. **Start ngrok for Slack Events**
   ```bash
   ngrok http 8080
   ```

## Testing

1. **Run Unit Tests**
   ```bash
   poetry run pytest tests/unit
   ```

2. **Run Integration Tests**
   ```bash
   poetry run pytest tests/integration
   ```

3. **Run E2E Tests**
   ```bash
   poetry run pytest tests/e2e
   ```

## Deployment

1. **Deploy to Firebase**
   ```bash
   firebase deploy --only functions
   ```

2. **Update Slack Event URL**
   - Use Firebase function URL
   - Verify endpoint in Slack

## Monitoring

1. **Firebase Console**
   - View function logs
   - Monitor Firestore usage
   - Check performance metrics

2. **Slack App Dashboard**
   - Event delivery status
   - Bot user online status

3. **OpenAI Dashboard**
   - API usage
   - Token consumption
   - Error rates

## Troubleshooting

### Common Issues

1. **Cold Start Latency**
   - Check function memory allocation
   - Verify dependency optimization

2. **Slack Event Timeouts**
   - Monitor function execution time
   - Check API call latencies

3. **Task Extraction Failures**
   - Review OpenAI API responses
   - Check prompt formatting

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
poetry run python -m src.main --debug
```

## Security Notes

1. Never commit `.env` file
2. Rotate API keys regularly
3. Monitor API usage and costs
4. Review Firebase security rules
5. Keep dependencies updated 