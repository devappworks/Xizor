# Environment Variables Template

Copy the contents below to a new file named `.env` in the project root directory and replace the placeholder values with your actual API credentials.

```dotenv
# Slack API credentials
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# Freedcamp API credentials
FREEDCAMP_API_KEY=your-api-key-here
FREEDCAMP_API_SECRET=your-api-secret-here
FREEDCAMP_PROJECT_ID=your-project-id-here

# Other configuration
OPENAI_API_KEY=your-openai-api-key
```

## Getting FreedCamp API Credentials

1. Log in to your FreedCamp account
2. Go to User Settings > API 
3. Generate an API key and secret
4. Find your project ID from the URL when viewing your project (or via the API)

## Setting up Slack Bot Token

1. Go to api.slack.com and create a new app
2. Add the following Bot Token Scopes:
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token (starts with `xoxb-`)
5. From the "Basic Information" page, copy the Signing Secret 