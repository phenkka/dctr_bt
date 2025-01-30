from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from logs.logging_config import logger

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event: types.Update, data: dict):
        # Логируем подключение к базе данных
        logger.debug(f"Passing database connection to handler: {self.pool}")
        data["db"] = self.pool
        return await handler(event, data)
