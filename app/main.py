import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from logs.logging_config import logger
from dotenv import load_dotenv
from bot.handlers import router
from bot.database import Database  # Импортируем класс Database
from bot.middleware import DatabaseMiddleware

load_dotenv()

bot = Bot(token=os.getenv('BOT_API'))
dp = Dispatcher()

# Создаем экземпляр класса Database
db = Database()

async def main():
    logger.info("🚀 Бот запускается...")

    # Инициализируем пул подключений к БД
    await db.init_pool()
    
    # Подключаем Middleware для передачи пула БД в хендлеры
    dp.update.middleware(DatabaseMiddleware(db.pool))
    
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    finally:
        # Закрываем пул подключений к БД при остановке
        await db.close_pool()
        logger.info("❌ Подключение к БД закрыто.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Бот остановлен вручную.")
        print("Выход")
