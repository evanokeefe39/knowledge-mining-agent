"""
Health check module for all integrated services.

Tests connectivity to databases, APIs, and other services used by the agent.
"""

import os
import requests
from pathlib import Path
from config import config
from log import setup_logger

logger = setup_logger(__name__)

def check_database():
    """Check Supabase PostgreSQL database connectivity."""
    try:
        import psycopg2

        user = config.get('SUPABASE__DB_USER')
        password = config.get('SUPABASE__DB_PASSWORD')
        host = config.get('SUPABASE__DB_HOST')
        port = config.get('SUPABASE__DB_PORT', 5432)
        dbname = config.get('SUPABASE__DB_NAME')

        if not all([user, password, host, dbname]):
            logger.error("Missing database connection parameters")
            return False

        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=dbname
        )
        cursor = conn.cursor()

        # Check connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"Connected to PostgreSQL: {version[0] if version else 'Unknown'}")

        # Check if dw schema exists
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'dw';")
        if cursor.fetchone():
            logger.info("Schema 'dw' exists")
        else:
            logger.warning("Schema 'dw' does not exist")

        cursor.close()
        conn.close()
        logger.info("Database health check passed")
        return True

    except ImportError:
        logger.error("psycopg2 not installed")
        return False
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def check_openai_api():
    """Check OpenAI API connectivity."""
    try:
        api_key = config.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not configured")
            return False

        # Simple API call to check connectivity
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info("OpenAI API health check passed")
            return True
        else:
            logger.error(f"OpenAI API returned status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"OpenAI API health check failed: {str(e)}")
        return False

def check_vector_store():
    """Check vector store table in Supabase."""
    try:
        import psycopg2

        user = config.get('SUPABASE__DB_USER')
        password = config.get('SUPABASE__DB_PASSWORD')
        host = config.get('SUPABASE__DB_HOST')
        port = config.get('SUPABASE__DB_PORT', 5432)
        dbname = config.get('SUPABASE__DB_NAME')
        table_name = config.get('VECTOR_STORE_TABLE', 'hormozi_transcripts')

        if not all([user, password, host, dbname]):
            logger.error("Missing database connection parameters")
            return False

        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=dbname
        )
        cursor = conn.cursor()

        # Check if pgvector extension is available
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if not cursor.fetchone():
            logger.warning("pgvector extension not found - vector operations may fail")
        else:
            logger.info("pgvector extension available")

        # Check if table exists (basic check)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """, (table_name,))
        exists = cursor.fetchone()[0]

        if exists:
            logger.info(f"Vector store table exists: {table_name}")
        else:
            logger.info(f"Vector store table will be created: {table_name}")

        cursor.close()
        conn.close()
        logger.info("Vector store health check passed")
        return True

    except ImportError:
        logger.error("psycopg2 not installed")
        return False
    except Exception as e:
        logger.error(f"Vector store health check failed: {str(e)}")
        return False

def health_check():
    """Run all health checks."""
    logger.info("Starting comprehensive health check...")

    checks = [
        ("Database", check_database),
        ("OpenAI API", check_openai_api),
        ("Vector Store", check_vector_store),
    ]

    results = {}
    for name, check_func in checks:
        logger.info(f"Checking {name}...")
        results[name] = check_func()

    # Summary
    passed = sum(results.values())
    total = len(results)

    logger.info(f"Health check complete: {passed}/{total} services healthy")

    if passed == total:
        logger.info("All health checks passed!")
        return True
    else:
        failed = [name for name, result in results.items() if not result]
        logger.error(f"Failed checks: {', '.join(failed)}")
        return False

if __name__ == "__main__":
    success = health_check()
    exit(0 if success else 1)