import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from telethon import TelegramClient
from telethon.tl.types import Message, PeerChannel, Channel, User

@pytest.fixture
def config():
    return {
        "channels": {
            "news_ai": [
                "@public_channel",
                "-1001234567890",
                "1234567891"
            ],
            "news_tech": [
                "@another_public",
                "-1009876543210"
            ],
            "target_channels": {
                "news_ai": "@target_ai",
                "news_tech": "@target_tech"
            }
        }
    }

@pytest.fixture
def mock_message():
    message = MagicMock(spec=Message)
    message.message = "Test message content"
    message.id = 123
    message.chat_id = -1001234567890
    return message

@pytest.fixture
def mock_channel():
    channel = MagicMock(spec=Channel)
    channel.id = -1001234567890
    channel.title = "Test Channel"
    channel.username = "testchannel"
    return channel

@pytest.fixture
def mock_client():
    client = AsyncMock(spec=TelegramClient)
    client.is_connected.return_value = True
    client.is_user_authorized.return_value = True
    return client
