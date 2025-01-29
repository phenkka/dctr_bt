from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event: types.Update, data: dict):
        # Передаем подключение к БД в данные хендлера
        data["db"] = self.pool
        return await handler(event, data)

