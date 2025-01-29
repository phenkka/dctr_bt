from aiogram import types
from aiogram.middleware.base import BaseMiddleware

class DatabaseMiddleware(BaseMiddleware):
    """Middleware для передачи соединения с базой данных в хендлеры"""

    def __init__(self, pool):
        self.pool = pool

    async def on_process_message(self, message: types.Message, data: dict):
        """Передаем пул в обработчики"""
        data['db_pool'] = self.pool
