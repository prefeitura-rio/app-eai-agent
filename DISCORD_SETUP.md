# Discord Notifications Setup

## Overview
The EAI Agent now sends Discord notifications when new prompt versions are uploaded in **production environment only**.

## Features
- 🚀 **Production Only**: Notifications are sent only when `ENVIRONMENT=production`
- 🧵 **Thread Support**: Messages can be sent to a specific Discord thread
- 🎨 **Rich Formatting**: Custom message formatting with embeds
- 📝 **Field Selection**: Shows only Version, Version Number, Author, Change Type, and Reason
- 🔧 **Dash to Linebreak**: Converts `-` in reason field to line breaks for better readability

## Required Environment Variables

### Production (Required)
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
DISCORD_THREAD_ID=YOUR_THREAD_ID  # Optional: sends to channel if not provided
ENVIRONMENT=production  # Must be set to "production" for notifications to work
```

### Optional Configuration
```bash
DISCORD_BOT_NAME="EAI Agent Notifications"  # Default bot name
DISCORD_BOT_AVATAR_URL="https://cdn.discordapp.com/embed/avatars/0.png"  # Default avatar
DISCORD_ENABLE_DEV_TESTING=false  # Set to "true" to enable notifications in development
```

## How It Works

1. **Trigger**: When a new prompt version is saved via `/api/v1/unified-save`
2. **Environment Check**: Only sends notifications if `ENVIRONMENT=production` (or `DISCORD_ENABLE_DEV_TESTING=true`)
3. **Message Format**: Sends a rich embed with selected fields
4. **Error Handling**: If Discord notification fails, the main operation continues normally

## Deployment

1. Set the required environment variables in your production environment
2. Deploy the application normally
3. Test by uploading a new prompt version through the frontend

## Message Example

```
🚀 New Prompt Version Created

Version: eai-2025-08-20-v1
Version Number: 1
Author: john.doe
Change Type: create
Reason: Initial setup
Fixed formatting issue
```

Note: The reason field automatically converts dashes to line breaks for better readability.
