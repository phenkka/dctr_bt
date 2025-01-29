import asyncpg
import os
from dotenv import load_dotenv
from logs.logging_config import logger

load_dotenv()

class Database:
    """Асинхронный класс для работы с PostgreSQL через asyncpg"""

    def __init__(self):
        """Инициализация класса, пул соединений создается в `init_pool()`"""
        self.pool = None

    async def init_pool(self):
        """Создает пул подключений"""
        self.pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'mydb'),
            user=os.getenv('POSTGRES_USER', 'myuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'mypassword')
        )
        logger.info("✅ Пул подключений к БД создан.")

    async def close_pool(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("❌ Пул подключений к БД закрыт.")

    async def execute_read_many(self, query, params=None):
        """Выполняет SELECT-запрос и возвращает список результатов"""
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(query, *params) if params else await conn.fetch(query)
                return [dict(row) for row in rows]  # Преобразуем в список словарей
            except Exception as e:
                logger.warning(f"⚠ Ошибка выполнения запроса: {e}")
                return []

    async def get_recommendation(self, data):
        """Получает рекомендации из БД на основе переданных данных"""
        query = """
            SELECT title, grade, text, servFreq, riskText
            FROM specific_recommendations
            WHERE 1=1
        """
        params = []

        if 'age' in data:
            query += " AND age_from <= $1 AND age_to >= $2"
            params.extend([data['age'], data['age']])

        if 'gender' in data:
            query += " AND (gender = $3 OR gender = 'men and women')"
            params.append(data['gender'])

        if data.get("smoking") == "yes":
            query += " OR (riskName = 'Tobacco user')"

        if data.get("pregnant") == "yes":
            query += " OR (riskName = 'Pregnant')"

        if data.get("sex") == "yes":
            query += " OR (riskName = 'Sexually Active')"

        results = await self.execute_read_many(query, params)
        return results if results else []