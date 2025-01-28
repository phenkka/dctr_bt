import psycopg2
import json
import os

db_host = os.getenv('POSTGRES_HOST', 'localhost')
db_port = os.getenv('POSTGRES_PORT', 5432)
db_name = os.getenv('POSTGRES_DB', 'mydb')
db_user = os.getenv('POSTGRES_USER', 'myuser')
db_password = os.getenv('POSTGRES_PASSWORD', 'mypassword')

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)
cursor = connection.cursor()

def create_tables():

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS specific_recommendations (
            id INTEGER PRIMARY KEY,
            title TEXT,
            grade TEXT,
            gender TEXT,
            text TEXT,
            age_from INTEGER,
            age_to INTEGER,
            servFreq TEXT,
            riskName TEXT,
            riskText TEXT,
            bmi TEXT,
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            tool_id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            text TEXT,
            keywords TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS specific_recommendations_tools (
            specific_recommendation_id INTEGER,
            tool_id INTEGER,
            FOREIGN KEY (specific_recommendation_id) REFERENCES specific_recommendations(id),
            FOREIGN KEY (tool_id) REFERENCES tools(tool_id),
            PRIMARY KEY (specific_recommendation_id, tool_id)
        )
    ''')


import json

def insert_data():
    with open('specific_recommendations.json', 'r', encoding='utf-8') as f:
        specific_recommendations = json.load(f)

    with open('tools.json', 'r', encoding='utf-8') as f:
        tools = json.load(f)

    for recommendation in specific_recommendations:
        if recommendation.get('grade', '') == "I":
            continue

        cursor.execute('SELECT id FROM specific_recommendations WHERE id = %s', (recommendation['id'],))
        existing = cursor.fetchone()
        if existing:
            print(f"Recommendation with id {recommendation['id']} already exists, skipping...")
        else:
            title = recommendation.get('title', '').split('--')[0]
            risk_text = recommendation.get('riskText', '')
            servFreq = recommendation.get('servFreq', '')
            text = recommendation.get('text', '').replace('The USPSTF', 'The DoctorAI', 1) #ЕСЛИ ЧТО, ТО ДОКТОРОАИ ПОМЕНЯТЬ
            bmi = recommendation.get('bmi', '')

            cursor.execute('''
                INSERT INTO specific_recommendations (id, title, grade, gender, text, age_from, age_to, servFreq, riskName, riskText, bmi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                recommendation['id'],
                title,
                recommendation['grade'],
                recommendation['gender'],
                text,
                recommendation['ageRange'][0],  
                recommendation['ageRange'][1],  
                servFreq,
                recommendation['riskName'],
                risk_text,
                bmi
            ))


    for tool_id, tool in tools.items():

        cursor.execute('SELECT tool_id FROM tools WHERE tool_id = %s', (tool_id,))
        existing = cursor.fetchone()
        if existing:
            print(f"Tool with id {tool_id} already exists, skipping...")
        else:
            cursor.execute('''
                INSERT INTO tools (tool_id, url, title, text, keywords)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                int(tool_id),
                tool['url'],
                tool['title'],
                tool['text'],
                tool['keywords']
            ))
            print(f"Inserted tool with id {tool_id}")

    for recommendation in specific_recommendations:
        for tool_id in recommendation['tool']:

            cursor.execute('''
                SELECT 1 FROM specific_recommendations_tools
                WHERE specific_recommendation_id = %s AND tool_id = %s
            ''', (recommendation['id'], tool_id))
            existing = cursor.fetchone()
            if existing:
                print(f"Link between recommendation {recommendation['id']} and tool {tool_id} already exists, skipping...")
            else:
                cursor.execute('''
                    INSERT INTO specific_recommendations_tools (specific_recommendation_id, tool_id)
                    VALUES (%s, %s)
                ''', (recommendation['id'], tool_id))
                print(f"Inserted link between recommendation {recommendation['id']} and tool {tool_id}")

    connection.commit()



# Основной блок
if __name__ == "__main__":
    create_tables()
    insert_data()

    cursor.close()
    connection.close()
