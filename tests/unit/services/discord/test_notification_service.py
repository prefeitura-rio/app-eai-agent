import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.discord.notification_service import (
    DiscordNotificationService,
    DiscordMessage,
    DiscordEmbed,
    discord_service
)


class TestDiscordNotificationService:
    """Test cases for Discord notification service."""
    
    def test_is_production_true(self):
        """Test is_production returns True for production environments."""
        service = DiscordNotificationService()
        service.environment = "production"
        assert service.is_production() is True
        
        service.environment = "prod"
        assert service.is_production() is True
        
        service.environment = "PRODUCTION"
        assert service.is_production() is True
    
    def test_is_production_false(self):
        """Test is_production returns False for non-production environments."""
        service = DiscordNotificationService()
        service.environment = "development"
        assert service.is_production() is False
        
        service.environment = "staging"
        assert service.is_production() is False
        
        service.environment = "test"
        assert service.is_production() is False
    
    def test_is_configured_true(self):
        """Test is_configured returns True when webhook URL is set."""
        service = DiscordNotificationService()
        service.webhook_url = "https://discord.com/api/webhooks/123/abc"
        assert service.is_configured() is True
    
    def test_is_configured_false(self):
        """Test is_configured returns False when webhook URL is not set."""
        service = DiscordNotificationService()
        service.webhook_url = None
        assert service.is_configured() is False
        
        service.webhook_url = ""
        assert service.is_configured() is False
    
    @pytest.mark.asyncio
    async def test_send_notification_not_configured(self):
        """Test notification is skipped when not configured."""
        service = DiscordNotificationService()
        service.webhook_url = None
        
        message = DiscordMessage(content="test")
        result = await service.send_notification(message)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_not_production(self):
        """Test notification is skipped when not in production."""
        service = DiscordNotificationService()
        service.webhook_url = "https://discord.com/api/webhooks/123/abc"
        service.environment = "development"
        
        message = DiscordMessage(content="test")
        result = await service.send_notification(message)
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_notification_success(self, mock_client):
        """Test successful notification sending."""
        # Setup
        service = DiscordNotificationService()
        service.webhook_url = "https://discord.com/api/webhooks/123/abc"
        service.environment = "production"
        
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        message = DiscordMessage(content="test message")
        
        # Execute
        result = await service.send_notification(message)
        
        # Assert
        assert result is True
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_notification_failure(self, mock_client):
        """Test failed notification sending."""
        # Setup
        service = DiscordNotificationService()
        service.webhook_url = "https://discord.com/api/webhooks/123/abc"
        service.environment = "production"
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        message = DiscordMessage(content="test message")
        
        # Execute
        result = await service.send_notification(message)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_send_notification_exception(self, mock_client):
        """Test notification sending with exception."""
        # Setup
        service = DiscordNotificationService()
        service.webhook_url = "https://discord.com/api/webhooks/123/abc"
        service.environment = "production"
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("Network error")
        )
        
        message = DiscordMessage(content="test message")
        
        # Execute
        result = await service.send_notification(message)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    @patch('src.services.discord.notification_service.DiscordNotificationService.send_notification')
    async def test_send_prompt_version_notification(self, mock_send):
        """Test prompt version notification creation and sending."""
        # Setup
        mock_send.return_value = True
        service = DiscordNotificationService()
        
        # Execute
        result = await service.send_prompt_version_notification(
            agent_type="test_agent",
            version_number=1,
            version_display="eai-2025-08-20-v1",
            author="test_user",
            reason="Testing notification",
            change_type="prompt",
            prompt_content_preview="This is a test prompt"
        )
        
        # Assert
        assert result is True
        mock_send.assert_called_once()
        
        # Check the message structure
        call_args = mock_send.call_args[0][0]
        assert isinstance(call_args, DiscordMessage)
        assert len(call_args.embeds) == 1
        
        embed = call_args.embeds[0]
        assert embed.title == "🚀 New Prompt Version Deployed"
        assert len(embed.fields) >= 6  # Should have at least 6 fields
    
    @pytest.mark.asyncio
    @patch('src.services.discord.notification_service.DiscordNotificationService.send_notification')
    async def test_send_prompt_version_notification_with_long_content(self, mock_send):
        """Test prompt version notification with long prompt content."""
        # Setup
        mock_send.return_value = True
        service = DiscordNotificationService()
        
        long_prompt = "A" * 1000  # 1000 character prompt
        
        # Execute
        result = await service.send_prompt_version_notification(
            agent_type="test_agent",
            version_number=1,
            version_display="eai-2025-08-20-v1",
            author="test_user",
            reason="Testing with long content",
            change_type="prompt",
            prompt_content_preview=long_prompt
        )
        
        # Assert
        assert result is True
        mock_send.assert_called_once()
        
        # Check that prompt preview was truncated
        call_args = mock_send.call_args[0][0]
        embed = call_args.embeds[0]
        prompt_field = next(field for field in embed.fields if field["name"] == "📄 Prompt Preview")
        assert len(prompt_field["value"]) <= 506  # 500 + "..." + code block formatting


class TestDiscordMessage:
    """Test cases for Discord message data classes."""
    
    def test_discord_embed_to_dict(self):
        """Test DiscordEmbed to_dict method."""
        embed = DiscordEmbed(
            title="Test Title",
            description="Test Description",
            color=0x00ff00,
            timestamp="2025-01-01T00:00:00Z",
            fields=[{"name": "Field", "value": "Value", "inline": True}],
            footer={"text": "Footer"}
        )
        
        result = embed.to_dict()
        
        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"
        assert result["color"] == 0x00ff00
        assert result["timestamp"] == "2025-01-01T00:00:00Z"
        assert result["fields"] == [{"name": "Field", "value": "Value", "inline": True}]
        assert result["footer"] == {"text": "Footer"}
    
    def test_discord_message_to_dict(self):
        """Test DiscordMessage to_dict method."""
        embed = DiscordEmbed(title="Test", description="Test")
        message = DiscordMessage(
            content="Test content",
            embeds=[embed],
            username="Test Bot",
            avatar_url="https://example.com/avatar.png"
        )
        
        result = message.to_dict()
        
        assert result["content"] == "Test content"
        assert len(result["embeds"]) == 1
        assert result["embeds"][0]["title"] == "Test"
        assert result["username"] == "Test Bot"
        assert result["avatar_url"] == "https://example.com/avatar.png"
    
    def test_discord_message_minimal(self):
        """Test DiscordMessage with minimal data."""
        message = DiscordMessage(content="Just content")
        
        result = message.to_dict()
        
        assert result == {"content": "Just content"}


class TestGlobalInstance:
    """Test the global discord_service instance."""
    
    def test_global_instance_exists(self):
        """Test that global discord_service instance exists."""
        assert discord_service is not None
        assert isinstance(discord_service, DiscordNotificationService)
