import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from bot.handlers import router
from logs.logging_config import logger
from dotenv import load_dotenv

load_dotenv() 

bot = Bot(token=os.getenv('BOT_API'))

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