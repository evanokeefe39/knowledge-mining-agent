import os
import psycopg2
from dotenv import load_dotenv

def health_check():
    load_dotenv()

    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv('host')
    port = os.getenv('port')
    dbname = os.getenv('dbname')

    if not all([user, password, host, port, dbname]):
        print("Error: Missing database connection parameters in .env file")
        return False

    try:
        conn = psycopg2.connect(user=user, password=password, host=host, port=port, database=dbname)
        cursor = conn.cursor()

        # Check connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        if version:
            print(f"Connected to PostgreSQL: {version[0]}")
        else:
            print("Failed to retrieve version.")

        # Check if dw schema exists
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'dw';")
        if cursor.fetchone():
            print("Schema 'dw' exists.")
        else:
            print("Warning: Schema 'dw' does not exist.")

        cursor.close()
        conn.close()
        print("Health check passed: Connection to Supabase data warehouse confirmed.")
        return True

    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    health_check()