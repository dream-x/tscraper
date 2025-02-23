import os
import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    load_dotenv()

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if not api_id or not api_id.isdigit():
        logger.error("API_ID must be a valid integer")
        return

    if not api_hash:
        logger.error("API_HASH is required")
        return

    logger.info("Starting authentication process...")
    client = TelegramClient('my_user_session', int(api_id), api_hash)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            logger.info("Please enter your phone number in international format (e.g., +1234567890):")
            phone = input()
            await client.send_code_request(phone)

            logger.info("Please enter the code you received:")
            code = input()
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                logger.info("Two-factor authentication is enabled. Please enter your password:")
                password = input()
                await client.sign_in(password=password)

        logger.info("Successfully authenticated!")
        logger.info("Session file 'my_user_session.session' has been created")

        me = await client.get_me()
        logger.info(f"Logged in as: {me.first_name} (@{me.username})")

    except Exception as e:
        logger.error(f"Error during authentication: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
