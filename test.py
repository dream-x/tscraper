import asyncio
from telethon import TelegramClient

API_ID = 123456
API_HASH = "abcdef123456"

client = TelegramClient("my_session", API_ID, API_HASH)

async def main():
    await client.start()
    # do stuff
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())