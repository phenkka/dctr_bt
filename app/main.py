import asyncio
import logging

from aiogram import Bot, Dispatcher

import app.config as cfg
from app.handlers import router
from logs.logging_config import logger

bot = Bot(token=cfg.BOT_API)
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