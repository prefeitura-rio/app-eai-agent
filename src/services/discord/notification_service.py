from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
from loguru import logger

from src.config.env import DISCORD_WEBHOOK_URL, DISCORD_THREAD_ID, DISCORD_BOT_NAME, DISCORD_BOT_AVATAR_URL, DISCORD_ENABLE_DEV_TESTING, ENVIRONMENT


@dataclass
class DiscordEmbed:
    """Discord embed structure for rich messages."""
    title: str
    description: str
    color: int = 0x00ff00  # Green color
    timestamp: Optional[str] = None
    fields: Optional[list] = None
    footer: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert embed to dictionary format for Discord API."""
        embed = {
            "title": self.title,
            "description": self.description,
            "color": self.color,
        }
        
        if self.timestamp:
            embed["timestamp"] = self.timestamp
        
        if self.fields:
            embed["fields"] = self.fields
            
        if self.footer:
            embed["footer"] = self.footer
            
        return embed


@dataclass
class DiscordMessage:
    """Discord message structure."""
    content: Optional[str] = None
    embeds: Optional[list] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format for Discord API."""
        message = {}
        
        if self.content:
            message["content"] = self.content
            
        if self.embeds:
            message["embeds"] = [embed.to_dict() if isinstance(embed, DiscordEmbed) else embed for embed in self.embeds]
            
        if self.username:
            message["username"] = self.username
            
        if self.avatar_url:
            message["avatar_url"] = self.avatar_url
            
        return message


class DiscordNotificationService:
    """Service for sending Discord notifications."""
    
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
        self.thread_id = DISCORD_THREAD_ID
        self.environment = ENVIRONMENT
        self.enable_dev_testing = DISCORD_ENABLE_DEV_TESTING
        self.bot_name = DISCORD_BOT_NAME
        self.bot_avatar_url = DISCORD_BOT_AVATAR_URL
        
    def is_production(self) -> bool:
        """Check if the current environment is production."""
        return self.environment.lower() in ["production", "prod"]
    
    def should_send_notification(self) -> bool:
        """Check if notifications should be sent (production or dev testing enabled)."""
        return self.is_production() or self.enable_dev_testing
    
    def is_configured(self) -> bool:
        """Check if Discord webhook is properly configured."""
        return bool(self.webhook_url)
    
    def format_reason_with_breaks(self, reason: str) -> str:
        """
        Format reason text with line breaks at dashes for better Discord readability.
        
        Args:
            reason: The reason text to format
            
        Returns:
            str: Formatted reason with line breaks and bullet points
        """
        if not reason:
            return reason
            
        # Handle different dash patterns and convert to bullet points
        formatted = reason
        
        # Replace various dash patterns with line breaks and bullet points
        patterns = [
            " - ",  # space-dash-space
            "- ",   # dash-space at start of sentences
            " -",   # space-dash at end (less common)
        ]
        
        for pattern in patterns:
            if pattern in formatted:
                # Split by the pattern and rejoin with line breaks and bullets
                parts = formatted.split(pattern)
                if len(parts) > 1:
                    # First part stays as is, subsequent parts get bullet points
                    formatted = parts[0]
                    for part in parts[1:]:
                        if part.strip():  # Only add non-empty parts
                            formatted += f"\n• {part.strip()}"
                    break  # Use first matching pattern
        
        return formatted
        """
        Get the webhook URL, optionally with thread ID parameter.
        
        Returns:
            str: The complete webhook URL
        """
        if not self.webhook_url:
            return ""
            
        url = self.webhook_url
        
        # If thread ID is configured, add it as a query parameter
        if self.thread_id:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}thread_id={self.thread_id}"
            
        return url
    
    async def send_notification(self, message: DiscordMessage) -> bool:
        """
        Send a notification to Discord.
        
        Args:
            message: DiscordMessage object to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_configured():
            logger.warning("Discord webhook URL not configured, skipping notification")
            return False
            
        if not self.should_send_notification():
            logger.info(f"Notifications disabled for environment ({self.environment}). Set DISCORD_ENABLE_DEV_TESTING=true for development testing.")
            return False
            
        try:
            webhook_url = self.get_webhook_url()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=message.to_dict(),
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                
                if response.status_code == 204:  # Discord returns 204 for successful webhook
                    logger.info("Discord notification sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send Discord notification: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
    
    async def send_prompt_version_notification(
        self,
        agent_type: str,
        version_number: int,
        version_display: str,
        author: str,
        reason: str,
        change_type: str,
        prompt_content_preview: Optional[str] = None
    ) -> bool:
        """
        Send a notification about a new prompt version.
        
        Args:
            agent_type: Type of the agent
            version_number: Version number
            version_display: Display version (e.g., eai-2025-08-20-v1)
            author: Author of the change
            reason: Reason for the change
            change_type: Type of change (prompt, config, both)
            prompt_content_preview: Optional preview of prompt content
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Format reason with line breaks at dashes for better readability
        formatted_reason = self.format_reason_with_breaks(reason)
        
        # Create embed with simplified version information (only requested fields)
        embed = DiscordEmbed(
            title="🚀 Nova Versão do Prompt Implantada",
            description=f"Uma nova versão do prompt subiu para **produção**",
            color=0x00ff00,  # Green color for production deployments
            timestamp=datetime.utcnow().isoformat(),
            fields=[
                {
                    "name": "📦 Versão",
                    "value": f"`{version_display}`",
                    "inline": True
                },
                {
                    "name": "🔢 Número da Versão",
                    "value": f"`{version_number}`",
                    "inline": True
                },
                {
                    "name": "👤 Autor",
                    "value": f"`{author}`",
                    "inline": True
                },
                {
                    "name": "🔄 Tipo de Mudança",
                    "value": f"`{change_type}`",
                    "inline": True
                },
                {
                    "name": "📝 Motivo",
                    "value": formatted_reason[:1000] if len(formatted_reason) > 1000 else formatted_reason,  # Discord field limit
                    "inline": False
                }
            ],
            footer={
                "text": "EAI Agent • Produção",
                "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
        )
        
        # No longer including prompt preview - only the 5 requested fields
        message = DiscordMessage(
            embeds=[embed],
            username=self.bot_name,
            avatar_url=self.bot_avatar_url
        )
        
        return await self.send_notification(message)


# Global instance
discord_service = DiscordNotificationService()
