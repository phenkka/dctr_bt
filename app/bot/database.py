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
        """Создает пул подключений и выполняет создание таблиц"""
        self.pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'mydb'),
            user=os.getenv('POSTGRES_USER', 'myuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'mypassword')
        )
        logger.info("✅ Пул подключений к БД создан.")

        # Создаем таблицы
        await self.create_tables()

    async def create_tables(self):
        """Создание необходимых таблиц в базе данных"""
        create_tables_query = """
        CREATE TABLE IF NOT EXISTS specific_recommendations (
            id SERIAL PRIMARY KEY,
            title TEXT,
            grade TEXT,
            gender TEXT,
            text TEXT,
            age_from INT,
            age_to INT,
            servFreq TEXT,
            riskName TEXT,
            riskText TEXT,
            bmi TEXT
        );

        CREATE TABLE IF NOT EXISTS tools (
            tool_id INT PRIMARY KEY,
            url TEXT,
            title TEXT,
            text TEXT,
            keywords TEXT
        );

        CREATE TABLE IF NOT EXISTS specific_recommendations_tools (
            specific_recommendation_id INT REFERENCES specific_recommendations(id),
            tool_id INT REFERENCES tools(tool_id),
            PRIMARY KEY (specific_recommendation_id, tool_id)
        );
        """
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(create_tables_query)
                logger.info("✅ Таблицы в базе данных успешно созданы.")
            except Exception as e:
                logger.warning(f"⚠ Ошибка при создании таблиц: {e}")

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