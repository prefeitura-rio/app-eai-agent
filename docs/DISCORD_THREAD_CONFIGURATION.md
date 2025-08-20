# Discord Thread Notifications Configuration

## 🧵 **Thread Support Overview**

The Discord notification system supports sending messages to specific threads instead of the main channel. This is useful for organizing notifications and keeping them from cluttering the main channel.

## 📋 **Configuration Methods**

### **Method 1: Thread ID in Webhook URL (Simplest)**

Include the thread ID directly in the webhook URL:

```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN?thread_id=YOUR_THREAD_ID"
```

**Example:**
```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1407728121104437288/ku9OG7E4Dk95ViJat5Y02eSitsf1G-on6WOUjZz5yuMZTIXIBI9UWayO97oSZ9mqG5Yb?thread_id=1407726510172803175"
```

### **Method 2: Separate Thread ID Variable (More Flexible)**

Set the webhook URL and thread ID separately:

```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN"
DISCORD_THREAD_ID="YOUR_THREAD_ID"
```

**Example:**
```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1407728121104437288/ku9OG7E4Dk95ViJat5Y02eSitsf1G-on6WOUjZz5yuMZTIXIBI9UWayO97oSZ9mqG5Yb"
DISCORD_THREAD_ID="1407726510172803175"
```

## 🔍 **How to Find Thread ID**

### **Method 1: Developer Mode (Recommended)**
1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Developer Mode (toggle on)
2. Right-click on the thread name
3. Select "Copy Thread ID"

### **Method 2: Browser URL**
1. Open Discord in web browser
2. Navigate to the thread
3. Copy the thread ID from the URL:
   ```
   https://discord.com/channels/SERVER_ID/CHANNEL_ID/THREAD_ID
                                                     ^^^^^^^^^^^
   ```

### **Method 3: Discord API**
Use Discord's API to list threads in a channel (for programmatic access).

## 🎛️ **Complete Configuration Options**

```bash
# Discord Channel/Thread Configuration
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
DISCORD_THREAD_ID="YOUR_THREAD_ID"                    # Optional: specific thread

# Bot Appearance Configuration  
DISCORD_BOT_NAME="EAI Agent Bot"                       # Bot display name
DISCORD_BOT_AVATAR_URL="https://your-avatar-url.png"  # Bot avatar image

# Environment Configuration
ENVIRONMENT="production"                               # Only sends in production
```

## 🎯 **Behavior Summary**

| Configuration | Behavior |
|---------------|----------|
| No thread ID | Messages sent to main channel |
| Thread ID in URL | Messages sent to specified thread |
| Separate DISCORD_THREAD_ID | Messages sent to specified thread |
| Both configured | DISCORD_THREAD_ID takes precedence |

## 🧪 **Testing Thread Configuration**

Use the provided test script to verify your thread setup:

```bash
# Test with current configuration
uv run python scripts/simple_discord_thread_test.py
```

The test script will:
- ✅ Verify thread configuration
- ✅ Show final webhook URL with thread parameters
- ✅ Send a test notification to the thread
- ✅ Provide troubleshooting information

## ✅ **Verification Checklist**

- [ ] Discord webhook created and URL copied
- [ ] Thread created and thread ID copied
- [ ] Environment variables configured
- [ ] Test script runs successfully
- [ ] Test message appears in correct thread (not main channel)
- [ ] Bot name and avatar display correctly

## 🔧 **Advanced Thread Management**

### **Creating Threads Programmatically**

If you need to create threads automatically, you can use Discord's API:

```python
# Example: Create a thread for notifications
POST https://discord.com/api/v10/channels/{channel_id}/threads
{
    "name": "EAI Agent Notifications",
    "type": 11,  # Public thread
    "auto_archive_duration": 1440  # Archive after 24 hours of inactivity
}
```

### **Thread Types**
- **Public Thread** (type 11): Visible to all channel members
- **Private Thread** (type 12): Only visible to invited members
- **Announcement Thread** (type 10): For announcement channels

### **Thread Auto-Archiving**
Threads automatically archive after inactivity. Options:
- 60 minutes
- 24 hours (1440 minutes)
- 3 days (4320 minutes)
- 7 days (10080 minutes)

## 🚨 **Important Notes**

1. **Thread Permissions**: Ensure the webhook has permission to post in threads
2. **Archived Threads**: Messages to archived threads will fail
3. **Thread Limits**: Servers have limits on active threads
4. **Fallback**: If thread posting fails, consider fallback to main channel

## 🔄 **Migration from Channel to Thread**

To migrate existing notifications from a channel to a thread:

1. **Create the thread** in your notification channel
2. **Copy the thread ID** using developer mode
3. **Update your environment variables** with the thread ID
4. **Test the configuration** using the test script
5. **Deploy to production** with the new configuration

## 📞 **Troubleshooting Thread Issues**

### **Messages Not Appearing in Thread**
- Verify thread ID is correct
- Check thread is not archived
- Ensure webhook has thread permissions
- Test with main channel first

### **Thread ID Not Working**
- Verify you copied the thread ID, not message ID
- Check the thread exists and is accessible
- Try the thread ID in Discord's URL manually

### **Bot Permissions**
- Webhook needs "Send Messages" permission
- Webhook needs "Send Messages in Threads" permission
- Check server and channel permission overrides

The thread notification system is now fully configured and tested! 🚀
