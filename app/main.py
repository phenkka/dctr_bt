import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from app.config import BOT_API
from app.bot.handlers import router
from app.logs.logging_config import logger

# BOT_API = os.getenv("BOT_API")

bot = Bot(token=BOT_API)
dp = Dispatcher()

async def main():
    logger.info("Bot is started. Polling begins.")
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot is stopped manually.")
        print("Exit")