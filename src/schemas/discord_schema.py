from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiscordEmbedField(BaseModel):
    """Discord embed field schema."""
    name: str = Field(..., max_length=256, description="Field name")
    value: str = Field(..., max_length=1024, description="Field value")
    inline: Optional[bool] = Field(False, description="Whether field should be inline")


class DiscordEmbedFooter(BaseModel):
    """Discord embed footer schema."""
    text: str = Field(..., max_length=2048, description="Footer text")
    icon_url: Optional[str] = Field(None, description="Footer icon URL")


class DiscordEmbedSchema(BaseModel):
    """Discord embed schema."""
    title: Optional[str] = Field(None, max_length=256, description="Embed title")
    description: Optional[str] = Field(None, max_length=4096, description="Embed description")
    color: Optional[int] = Field(None, description="Embed color as integer")
    timestamp: Optional[datetime] = Field(None, description="Embed timestamp")
    fields: Optional[List[DiscordEmbedField]] = Field(None, max_items=25, description="Embed fields")
    footer: Optional[DiscordEmbedFooter] = Field(None, description="Embed footer")


class DiscordWebhookMessage(BaseModel):
    """Discord webhook message schema."""
    content: Optional[str] = Field(None, max_length=2000, description="Message content")
    embeds: Optional[List[DiscordEmbedSchema]] = Field(None, max_items=10, description="Message embeds")
    username: Optional[str] = Field(None, max_length=80, description="Override webhook username")
    avatar_url: Optional[str] = Field(None, description="Override webhook avatar URL")


class PromptVersionNotificationData(BaseModel):
    """Data for prompt version notification."""
    agent_type: str = Field(..., description="Type of the agent")
    version_number: int = Field(..., description="Version number")
    version_display: str = Field(..., description="Display version string")
    author: str = Field(..., description="Author of the change")
    reason: str = Field(..., description="Reason for the change")
    change_type: str = Field(..., description="Type of change (prompt, config, both)")
    prompt_content_preview: Optional[str] = Field(None, description="Preview of prompt content")
    environment: str = Field(default="production", description="Environment where change was made")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the change was made")
