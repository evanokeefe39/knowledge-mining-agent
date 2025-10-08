"""
Database module for the knowledge mining agent.

Provides a simple get_db() function to get a configured database client.
"""

import psycopg2
from psycopg2 import pool
from config import config


# Connection pool for reuse
_db_pool = None


def get_db():
    """Get a configured database connection.

    Returns:
        psycopg2 connection object
    """
    global _db_pool

    if _db_pool is None:
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

    return _db_pool.getconn()


def close_db(conn):
    """Return connection to pool.

    Args:
        conn: psycopg2 connection object
    """
    global _db_pool
    if _db_pool:
        _db_pool.putconn(conn)