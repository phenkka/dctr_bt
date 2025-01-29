import json
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Данные для подключения к БД
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'mydb')
DB_USER = os.getenv('POSTGRES_USER', 'myuser')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'mypassword')


async def insert_data():
    """Функция для заполнения БД из JSON-файлов"""
    
    # Создаем пул подключений
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    async with pool.acquire() as conn:
        async with conn.transaction():  # Автоматический коммит в конце
            # Загружаем JSON-файлы
            with open('data/specific_recommendations.json', 'r', encoding='utf-8') as f:
                specific_recommendations = json.load(f)

            with open('data/tools.json', 'r', encoding='utf-8') as f:
                tools = json.load(f)

            # Вставка рекомендаций
            for recommendation in specific_recommendations:
                if recommendation.get('grade', '') == "I":
                    continue

                existing = await conn.fetchval(
                    'SELECT id FROM specific_recommendations WHERE id = $1',
                    recommendation['id']
                )
                if existing:
                    print(f"Recommendation with id {recommendation['id']} already exists, skipping...")
                else:
                    title = recommendation.get('title', '').split('--')[0]
                    risk_text = recommendation.get('riskText', '')
                    serv_freq = recommendation.get('servFreq', '')
                    text = recommendation.get('text', '').replace('The USPSTF', 'The DoctorAI', 1)  # Замена текста
                    bmi = recommendation.get('bmi', '')

                    await conn.execute('''
                        INSERT INTO specific_recommendations 
                        (id, title, grade, gender, text, age_from, age_to, servFreq, riskName, riskText, bmi)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ''', 
                        recommendation['id'],
                        title,
                        recommendation['grade'],
                        recommendation['gender'],
                        text,
                        recommendation['ageRange'][0],
                        recommendation['ageRange'][1],
                        serv_freq,
                        recommendation['riskName'],
                        risk_text,
                        bmi
                    )
                    print(f"Inserted recommendation with id {recommendation['id']}")

            # Вставка инструментов
            for tool_id, tool in tools.items():
                existing = await conn.fetchval(
                    'SELECT tool_id FROM tools WHERE tool_id = $1',
                    tool_id
                )
                if existing:
                    print(f"Tool with id {tool_id} already exists, skipping...")
                else:
                    await conn.execute('''
                        INSERT INTO tools (tool_id, url, title, text, keywords)
                        VALUES ($1, $2, $3, $4, $5)
                    ''', 
                        int(tool_id),
                        tool['url'],
                        tool['title'],
                        tool['text'],
                        tool['keywords']
                    )
                    print(f"Inserted tool with id {tool_id}")

            # Вставка связей между рекомендациями и инструментами
            for recommendation in specific_recommendations:
                for tool_id in recommendation.get('tool', []):
                    existing = await conn.fetchval('''
                        SELECT 1 FROM specific_recommendations_tools
                        WHERE specific_recommendation_id = $1 AND tool_id = $2
                    ''', recommendation['id'], tool_id)

                    if existing:
                        print(f"Link between recommendation {recommendation['id']} and tool {tool_id} already exists, skipping...")
                    else:
                        await conn.execute('''
                            INSERT INTO specific_recommendations_tools (specific_recommendation_id, tool_id)
                            VALUES ($1, $2)
                        ''', recommendation['id'], tool_id)
                        print(f"Inserted link between recommendation {recommendation['id']} and tool {tool_id}")

    await pool.close()  # Закрываем пул подключений


# Запуск скрипта
if __name__ == "__main__":
    asyncio.run(insert_data())
