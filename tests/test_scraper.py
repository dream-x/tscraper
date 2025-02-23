import pytest
from unittest.mock import AsyncMock, MagicMock
from tscraper.tscraper import TelegramScraper
from telethon.tl.types import Message, PeerChannel, Channel

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
    message.chat = MagicMock()
    message.chat.username = "public_channel"
    message.grouped_id = None
    message.media = None
    return message

@pytest.fixture
def mock_channel():
    channel = MagicMock(spec=Channel)
    channel.id = -1001234567890
    channel.title = "Test Channel"
    channel.username = "public_channel"
    return channel

@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.is_connected.return_value = True
    client.is_user_authorized.return_value = True
    return client

@pytest.mark.asyncio
async def test_handle_message(mock_client, mock_message, mock_channel, config):
    scraper = TelegramScraper(123, "hash", config)
    scraper.client = mock_client

    # Create event mock
    event = AsyncMock()
    event.message = mock_message

    # Setup get_chat() method
    chat = AsyncMock()
    chat.username = "public_channel"  # Matches the source channel in config
    chat.id = -1001234567890
    event.get_chat.return_value = chat

    await scraper._handle_message(event)

    # Verify forward_messages was called with correct target
    mock_client.forward_messages.assert_called_once_with("@target_ai", mock_message)

@pytest.mark.asyncio
async def test_handle_message_no_target(mock_client, mock_message, mock_channel, config):
    scraper = TelegramScraper(123, "hash", config)
    scraper.client = mock_client

    event = AsyncMock()
    event.message = mock_message

    chat = AsyncMock()
    chat.username = "unknown_channel"  # Channel not in config
    event.get_chat.return_value = chat

    await scraper._handle_message(event)

    # Verify forward_messages was not called
    mock_client.forward_messages.assert_not_called()

@pytest.mark.asyncio
async def test_message_handler_with_media(mock_client, config):
    scraper = TelegramScraper(123, "hash", config)
    scraper.client = mock_client

    # Create message with media
    message = MagicMock(spec=Message)
    message.media = MagicMock()
    message.message = "Test message with media"
    message.id = 123
    message.grouped_id = None

    # Create event
    event = AsyncMock()
    event.message = message

    # Setup get_chat() method
    chat = AsyncMock()
    chat.username = "public_channel"  # Matches the source channel in config
    chat.id = -1001234567890
    event.get_chat.return_value = chat

    await scraper._handle_message(event)
    mock_client.forward_messages.assert_called_once_with("@target_ai", message)

@pytest.mark.asyncio
async def test_message_handler_with_album(mock_client, config):
    scraper = TelegramScraper(123, "hash", config)
    scraper.client = mock_client

    grouped_id = "group1"
    messages = []

    # Create album messages
    for i in range(3):
        msg = MagicMock(spec=Message)
        msg.id = i + 1
        msg.grouped_id = grouped_id
        messages.append(msg)

    # Setup client.iter_messages
    mock_client.iter_messages.return_value = messages

    # Create event with first message
    event = AsyncMock()
    event.message = messages[0]

    chat = AsyncMock()
    chat.username = "public_channel"
    chat.id = -1001234567890
    event.get_chat.return_value = chat

    await scraper._handle_message(event)

    # Verify album forwarding
    mock_client.forward_messages.assert_called_once_with("@target_ai", messages)

@pytest.mark.asyncio
async def test_connect_unauthorized():
    config = {
        "channels": {
            "test": [],
            "target_channels": {"test": "@target"}
        }
    }
    scraper = TelegramScraper(123, "hash", config)
    client = AsyncMock()
    client.connect = AsyncMock()
    client.is_connected.return_value = True
    client.is_user_authorized.return_value = False

    scraper._setup_client = AsyncMock(return_value=client)
    assert await scraper._connect() == False

@pytest.mark.asyncio
async def test_connect_authorized(mock_client, config):
    scraper = TelegramScraper(123, "hash", config)

    # Setup mock client
    mock_client.is_user_authorized.return_value = True
    mock_client.connect = AsyncMock()
    mock_client.is_connected.return_value = True

    # Mock the _resolve_channels method
    scraper._resolve_channels = AsyncMock(return_value=["@channel1"])

    # Setup client creation
    scraper._setup_client = AsyncMock(return_value=mock_client)

    # Ensure message handler is properly set up
    @mock_client.on.return_value
    def message_handler(event):
        pass

    assert await scraper._connect() == True

    # Verify the connection process
    mock_client.connect.assert_called_once()
    mock_client.is_user_authorized.assert_called_once()
    assert scraper.connection_start_time is not None
