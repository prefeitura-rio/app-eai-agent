# Discord Notifications Setup

## Overview
The EAI Agent now sends Discord notifications when new prompt versions are uploaded in **production environment only**.

## Features
- 🚀 **Production Only**: Notifications are sent only when `ENVIRONMENT=production`
- 🧵 **Thread Support**: Messages can be sent to a specific Discord thread
- 🎨 **Rich Formatting**: Custom message formatting with embeds
- 📝 **Field Selection**: Shows Version, Version Number, Author, Change Type, Reason, and ClickUp Cards (when provided)
- 🔧 **Dash to Linebreak**: Converts `-` in reason field to line breaks for better readability
- 🎯 **ClickUp Cards**: Shows resolved ClickUp cards from the "ClickUp Cards" field in the frontend

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
4. **ClickUp Cards**: If the "ClickUp Cards" field is not empty, adds a "📋 Cards resolvidos" section
5. **Error Handling**: If Discord notification fails, the main operation continues normally

## Frontend Changes

- **Field Renamed**: "Memory Blocks" has been renamed to "ClickUp Cards" in the frontend
- **Purpose**: Use this field to list ClickUp cards that were resolved in the release
- **Format**: JSON array with objects containing `label` and `value` properties

## Deployment

1. Set the required environment variables in your production environment
2. Deploy the application normally
3. Test by uploading a new prompt version through the frontend with ClickUp cards

## Message Example

```
🚀 New Prompt Version Created

Version: eai-2025-08-26-v1
Version Number: 1
Author: john.doe
Change Type: create
Reason: Bug fixes and improvements
Fixed authentication issue
Enhanced performance

📋 Cards resolvidos
• **CARD-123**: Fixed authentication bug
• **CARD-124**: Added new search functionality
• **CARD-125**: Improved database performance
```

Note: The "Cards resolvidos" section only appears when ClickUp cards are provided in the frontend.
