from psycopg2 import pool

from app.logs.logging_config import logger

class Database:
    def __init__(self, min_conn, max_conn, dbname, user, password, host, port):
        self.connection_pool = pool.SimpleConnectionPool(
            min_conn,
            max_conn,
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        self.connection_pool.putconn()

    def close_all_connection(self):
        self.connection_pool.closeall()

    def execute_read_many_query(self, query, params=None):
        conn = self.get_connection()
        result = None
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    result = cursor.fetchall()
        except Exception as e:
            logger.warning(f"An error occurred: {e}")
        finally:
            self.release_connection(conn)
        return result

    def get_recommendation(self, data):
        query = """
            SELECT title, grade, text, servFreq, riskText
            FROM specific_recommendations
            WHERE 1=1
        """
        params = []

        if 'age' in data:
            query += " AND age_from <= %s AND age_to >= %s"
            params.extend([data['age'], data['age']])

        if 'gender' in data:
            query += " AND (gender = %s OR gender = 'men and women')"
            params.append(data['gender'])

        if data["smoking"] == "yes":
            query += " OR (riskName = 'Tobacco user')"

        if data["pregnant"] == "yes":
            query += " OR (riskName = 'Pregnant')"

        if data["sex"] == "yes":
            query += " OR (riskName = 'Sexually Active')"


        results = self.execute_read_many_query(query, params)

        # Преобразуем результат в список списков (если результат не None)
        return [list(row) for row in results] if results else []