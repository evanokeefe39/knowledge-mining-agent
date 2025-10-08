"""
Database module for the knowledge mining agent.

Provides a simple get_db() function to get a configured database client.
"""

import psycopg2
from psycopg2 import pool
from config import config
from log import setup_logger

logger = setup_logger(__name__)


# Connection pool for reuse
_db_pool = None


def get_db():
    """Get a configured database connection.

    Returns:
        psycopg2 connection object
    """
    global _db_pool

    if _db_pool is None:
        logger.info("Initializing database connection pool")
        # Initialize connection pool
        db_config = config.database
        connection_string = (
            f"postgresql://{db_config.user}:"
            f"{db_config.password}@"
            f"{db_config.host}:"
            f"{db_config.port}/"
            f"{db_config.name}"
        )
        _db_pool = pool.SimpleConnectionPool(1, 10, connection_string)

    logger.debug("Getting database connection from pool")
    return _db_pool.getconn()


def close_db(conn):
    """Return connection to pool.

    Args:
        conn: psycopg2 connection object
    """
    global _db_pool
    if _db_pool:
        logger.debug("Returning connection to pool")
        _db_pool.putconn(conn)


def test_connection():
    """Test database connection."""
    logger.info("Testing database connection")
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        logger.info(f"Connection successful: {result}")
        close_db(conn)
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False


def describe_schema():
    """Describe the database schema."""
    schema = config.database.schema
    logger.info(f"Describing {schema} schema")
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Get all tables in schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
        """, (schema,))
        tables = cursor.fetchall()

        if not tables:
            logger.warning(f"No tables found in {schema} schema")
            close_db(conn)
            return

        logger.info(f"Found {len(tables)} tables in {schema} schema")
        for (table_name,) in tables:
            logger.info(f"Table: {table_name}")

            # Get columns
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table_name))
            columns = cursor.fetchall()

            logger.debug("  Columns:")
            for col_name, data_type, nullable, default in columns:
                null_str = "NULL" if nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                logger.debug(f"    {col_name}: {data_type} {null_str}{default_str}")

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}")
                count = cursor.fetchone()[0]
                logger.info(f"  Row count: {count}")
            except Exception as e:
                logger.warning(f"  Row count error: {e}")

        close_db(conn)

    except Exception as e:
        logger.error(f"Schema inspection failed: {e}")