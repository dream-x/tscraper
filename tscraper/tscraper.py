import os
import sys
import asyncio
import time
import uvicorn
import yaml
import logging
from typing import Dict, List, Union
from pathlib import Path
from telethon import TelegramClient, events
from telethon.errors import TypeNotFoundError
from telethon.tl.types import PeerChannel
from datetime import datetime
from dotenv import load_dotenv
from .health import app, set_scraper_status
from .metrics import (
    scraper_connected,
    scraper_uptime_seconds,
    reconnect_total,
    messages_received_total,
    messages_forwarded_total,
    messages_failed_total,
    albums_forwarded_total,
    forward_duration_seconds,
    scraper_info,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    pass

def load_yaml_config() -> Dict:
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    if not Path(config_path).exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            if not config:
                raise ConfigError("Invalid config structure")
            # If config already contains channels, validate it
            if 'channels' in config:
                if not isinstance(config['channels'], dict):
                    raise ConfigError("Invalid config structure")
                if not config['channels'].get('target_channels'):
                    raise ConfigError("Missing target_channels in config")
                return config
            # If config starts with categories directly, wrap it in channels
            if not config.get('target_channels'):
                raise ConfigError("Missing target_channels in config")
            return {'channels': config}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML configuration: {e}")

class TelegramScraper:
    def __init__(self, api_id: int, api_hash: str, config: Dict):
        self.api_id = api_id
        self.api_hash = api_hash

        if 'channels' not in config:
            raise ConfigError("Invalid config structure: missing 'channels' key")

        self.config = config['channels']
        if 'target_channels' not in self.config:
            raise ConfigError("Invalid config structure: missing 'target_channels' in channels")

        self.target_channels = self.config['target_channels']
        self.client = None
        self.channel_cache = {}
        self.connection_start_time = None
        self.reconnect_delay = 1
        self.max_reconnect_delay = 30

    async def _resolve_channel(self, channel_str: str) -> Union[int, str]:
        """Convert channel string to internal ID or username."""
        if channel_str.startswith('-100'):
            return int(channel_str)
        elif channel_str.isdigit():
            return int(f'-100{channel_str}')
        return channel_str

    async def _resolve_channels(self) -> List[str]:
        """Get list of all source channels."""
        sources = []
        for category in self.config:
            if category != 'target_channels':
                sources.extend(self.config[category])
        logger.info(f"Monitoring channels: {sources}")
        return sources

    def _get_category_for_source(self, source: str) -> str | None:
        """Get category name for a source channel."""
        if isinstance(source, int):
            source = str(source)
        if not source.startswith('@'):
            source = f"@{source}"

        for category, channels in self.config.items():
            if category != 'target_channels':
                if source in channels:
                    return category
        return None

    async def _get_channel_info(self, channel_id: Union[int, str]) -> Dict:
        """Get channel title and username if available."""
        if channel_id in self.channel_cache:
            return self.channel_cache[channel_id]

        try:
            if isinstance(channel_id, int):
                entity = await self.client.get_entity(PeerChannel(channel_id))
            else:
                entity = await self.client.get_entity(channel_id)

            info = {
                'id': entity.id,
                'title': entity.title,
                'username': entity.username if hasattr(entity, 'username') else None
            }
            self.channel_cache[channel_id] = info
            return info
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None

    def _get_target_for_source(self, source: str) -> str:
        """Get target channel for source."""
        logger.info(f"Finding target for source: {source}")

        # Нормализуем source
        if isinstance(source, int):
            source = str(source)
        if not source.startswith('@'):
            source = f"@{source}"

        # Ищем в каждой категории
        for category, channels in self.config.items():
            if category != 'target_channels':
                if source in channels:
                    target = self.target_channels.get(category)
                    logger.info(f"Found target {target} in category {category}")
                    return target

        logger.warning(f"No target found for {source}")
        return None

    async def _handle_message(self, event):
        source = "<unknown>"
        category = "unknown"
        try:
            logger.info(f"Received message event")
            if not event.message:
                logger.warning("Event without message, skipping")
                return

            # Получаем информацию о канале
            chat = await event.get_chat()
            if not chat:
                logger.warning("Could not get chat info")
                return

            source = chat.username if chat.username else str(chat.id)
            category = self._get_category_for_source(source) or "unknown"
            messages_received_total.labels(category=category).inc()

            target = self._get_target_for_source(source)

            if not target:
                logger.warning(f"No target found for {source}")
                return

            t0 = time.monotonic()
            try:
                # Пробуем использовать send_message с file parameter для пересылки всего контента
                logger.info(f"Sending message from {source} to {target}")

                # Получаем все медиа из сообщения
                media = event.message.media
                grouped_media = event.message.grouped_id

                if grouped_media:
                    # Получаем сообщения из альбома, начиная с текущего ID
                    messages = []
                    current_msg_id = event.message.id

                    # Проверяем сообщения до и после текущего, чтобы собрать весь альбом
                    async for msg in self.client.iter_messages(
                        chat.id,
                        min_id=current_msg_id - 10,  # Проверяем 10 сообщений до
                        max_id=current_msg_id + 10,  # и 10 сообщений после
                        reverse=True
                    ):
                        if msg.grouped_id == grouped_media and msg.id not in [m.id for m in messages]:
                            messages.append(msg)

                    # Сортируем сообщения по ID чтобы сохранить порядок
                    messages.sort(key=lambda x: x.id)

                    # Проверяем что мы не обрабатывали это сообщение ранее
                    if event.message.id == messages[0].id:
                        # Пересылаем весь альбом только один раз
                        await self.client.forward_messages(target, messages)
                        albums_forwarded_total.labels(category=category).inc()
                        logger.info(f"Forwarded album with {len(messages)} messages")
                else:
                    # Если это одиночное сообщение, пересылаем как есть
                    await self.client.forward_messages(target, event.message)

                elapsed = time.monotonic() - t0
                forward_duration_seconds.observe(elapsed)
                messages_forwarded_total.labels(category=category).inc()
                logger.info(f"Successfully sent message from {source} to {target}")

            except Exception as e:
                logger.error(f"Error in message forwarding, trying alternative method: {e}")
                try:
                    # Fallback: отправляем текст + медиа отдельно
                    await self.client.send_message(
                        target,
                        event.message.message,
                        file=event.message.media,
                    )
                    elapsed = time.monotonic() - t0
                    forward_duration_seconds.observe(elapsed)
                    messages_forwarded_total.labels(category=category).inc()
                    logger.info(f"Fallback forwarding succeeded for {source} to {target}")
                except Exception as fallback_err:
                    messages_failed_total.labels(category=category).inc()
                    logger.error(f"Fallback forwarding also failed: {fallback_err}")

        except TypeNotFoundError:
            messages_failed_total.labels(category=category).inc()
            logger.warning(f"TypeNotFoundError when handling message from {source}")
        except Exception as e:
            messages_failed_total.labels(category=category).inc()
            logger.error(f"Error processing message: {e}", exc_info=True)


    async def _connect(self) -> bool:
        try:
            if not self.client:
                self.client = TelegramClient('my_user_session', self.api_id, self.api_hash)
                sources = await self._resolve_channels()
                logger.info(f"Resolved source channels: {sources}")

                @self.client.on(events.NewMessage(chats=sources))
                async def message_handler(event):
                    logger.info("Received new message event")
                    await self._handle_message(event)

                logger.info("Message handler registered")

            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.error("User is not authorized!")
                scraper_connected.set(0)
                set_scraper_status(connected=False, last_error="User not authorized")
                return False

            self.connection_start_time = datetime.now()
            scraper_connected.set(1)
            set_scraper_status(connected=True)
            logger.info(f"Connected successfully at {self.connection_start_time}")
            return True

        except Exception as e:
            logger.error(f"Connection attempt failed: {e}")
            scraper_connected.set(0)
            set_scraper_status(connected=False, last_error=str(e))
            if self.client:
                await self.client.disconnect()
            return False

    async def _setup_client(self):
        if not self.client:
            self.client = TelegramClient('my_user_session', self.api_id, self.api_hash)
        return self.client

    async def start(self):
        while True:
            try:
                if not self.client or not self.client.is_connected():
                    logger.info(f"Attempting to connect...")
                    reconnect_total.inc()
                    connected = await self._connect()

                    if not connected:
                        wait_time = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                        logger.info(f"Connection failed. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        self.reconnect_delay = wait_time
                        continue

                    self.reconnect_delay = 1
                    sources = await self._resolve_channels()
                    logger.info(f"Started monitoring {len(sources)} channels")

                if self.client:
                    await self.client.run_until_disconnected()

                # run_until_disconnected returned — connection dropped
                logger.warning("Disconnected from Telegram, will reconnect...")
                scraper_connected.set(0)
                set_scraper_status(connected=False, last_error="Disconnected")

            except Exception as e:
                logger.error(f"Connection error: {e}")
                scraper_connected.set(0)
                set_scraper_status(connected=False, last_error=str(e))
                if self.client:
                    try:
                        await self.client.disconnect()
                    except Exception:
                        pass
                wait_time = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                logger.info(f"Reconnecting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                self.reconnect_delay = wait_time

    async def _update_uptime(self):
        """Background task to update the uptime gauge."""
        while True:
            if self.connection_start_time:
                elapsed = (datetime.now() - self.connection_start_time).total_seconds()
                scraper_uptime_seconds.set(elapsed)
            await asyncio.sleep(15)

async def run_services(scraper: TelegramScraper, health_port: int):
    health_server = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=health_port,
            loop="asyncio"
        )
    )

    await asyncio.gather(
        scraper.start(),
        scraper._update_uptime(),
        health_server.serve()
    )

def main():
    try:
        load_dotenv()
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        health_port = int(os.getenv("HEALTH_PORT", "8000"))

        if not api_id or not api_id.isdigit():
            raise ConfigError("API_ID must be a valid integer")

        if not api_hash:
            raise ConfigError("API_HASH is required")

        config = load_yaml_config()

        scraper_info.info({
            'version': '0.2.0',
            'health_port': str(health_port),
        })

        scraper = TelegramScraper(int(api_id), api_hash, config)

        asyncio.run(run_services(scraper, health_port))
    except KeyboardInterrupt:
        logger.info("\nScraper stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
