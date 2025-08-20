# Discord Notifications Setup Guide

This document explains how to configure Discord notifications for prompt version uploads in production.

## Prerequisites

1. **Discord Server**: You need admin access to a Discord server where you want to receive notifications.
2. **Discord Webhook**: Create a webhook in your Discord channel.

## Setting up Discord Webhook

### Step 1: Create a Discord Webhook

1. Go to your Discord server
2. Right-click on the channel where you want notifications
3. Select "Edit Channel"
4. Go to "Integrations" tab
5. Click "Create Webhook"
6. Give it a name (e.g., "EAI Agent Bot")
7. Copy the webhook URL

### Step 2: Configure Environment Variables

Add the following environment variables to your production environment:

```bash
# Discord Configuration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
ENVIRONMENT=production
```

**Important Notes:**
- `DISCORD_WEBHOOK_URL`: The webhook URL you copied from Discord
- `ENVIRONMENT`: Must be set to "production" (or "prod") for notifications to be sent
- Notifications will NOT be sent in development, staging, or any other environment

## How It Works

### Production Only
- Discord notifications are ONLY sent when `ENVIRONMENT` is set to "production" or "prod"
- This prevents spam during development and testing

### Triggered Events
Notifications are sent when:
- A new prompt version is uploaded via the `/api/v1/unified-save` endpoint
- The change includes prompt content (change_type: "prompt" or "both")
- All environment checks pass

### Message Content
Each notification includes:
- 🤖 Agent Type
- 📦 Version Display Name (e.g., eai-2025-08-20-v1)
- 🔢 Version Number
- 👤 Author
- 🔄 Change Type (prompt, config, or both)
- 📝 Reason for change
- 📄 Prompt content preview (first 200 characters)
- ⏰ Timestamp

### Error Handling
- If Discord notification fails, it won't affect the prompt upload process
- Errors are logged but don't cause the main operation to fail
- Missing webhook URL or wrong environment will skip notifications silently

## Testing

### In Development
To test the notification service in development, temporarily set:
```bash
ENVIRONMENT=production
DISCORD_WEBHOOK_URL=your_test_webhook_url
```

**Remember to revert these changes after testing!**

### Verifying Configuration
You can check if Discord notifications are properly configured by looking at the logs:
- "Discord notification sent successfully" - Notification was sent
- "Discord webhook URL not configured, skipping notification" - Missing webhook URL
- "Not in production environment, skipping Discord notification" - Not in production
- "Failed to send Discord notification: ..." - Error occurred

## Security Considerations

1. **Webhook URL Security**: Treat the Discord webhook URL as a secret
2. **Environment Variables**: Store webhook URL in secure environment variable management
3. **Production Only**: Never set ENVIRONMENT=production in development environments
4. **Access Control**: Ensure only authorized personnel can modify prompt versions in production

## Troubleshooting

### No Notifications Received
1. Check if `ENVIRONMENT=production`
2. Verify `DISCORD_WEBHOOK_URL` is correctly set
3. Ensure the Discord webhook is still active
4. Check application logs for error messages

### Wrong Channel
- Verify the webhook URL points to the correct Discord channel
- Recreate the webhook if necessary

### Rate Limiting
- Discord webhooks have rate limits (30 requests per minute)
- If you hit limits, notifications may be delayed or dropped
- Consider batching notifications if you expect high volume

## Example Environment File

```bash
# Production Environment Variables
ENVIRONMENT=production
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz

# Other environment variables...
LETTA_API_URL=...
LETTA_API_TOKEN=...
# ... rest of your configuration
```
