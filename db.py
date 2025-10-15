"""
Database connection and introspection module.

This module provides utilities for connecting to the PostgreSQL database,
performing health checks, and introspecting database schema.
"""

import logging
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import config

# Setup logging
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager."""

    def __init__(self):
        self.connection = None
        self._load_config()

    def _load_config(self):
        """Load database configuration from config module."""
        try:
            # Assuming config has database settings
            self.db_config = {
                'host': config.settings.database.host,
                'port': config.settings.database.port,
                'database': config.settings.database.name,
                'user': config.settings.database.user,
                'password': config.settings.database.password,
            }
            self.default_schema = config.settings.database.default_schema
            logger.info("Database configuration loaded successfully")
        except AttributeError as e:
            logger.error(f"Database configuration not found in config: {e}")
            raise

    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True  # For introspection queries
            logger.info("Successfully connected to database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        result = {
            'status': 'unknown',
            'message': '',
            'details': {}
        }

        if not self.connection:
            result['status'] = 'disconnected'
            result['message'] = 'No active connection'
            return result

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Basic connectivity check
                cursor.execute("SELECT 1 as test")
                test_result = cursor.fetchone()

                # Get database info
                cursor.execute("SELECT current_database(), current_user, version()")
                db_info = cursor.fetchone()

                # Get connection count
                cursor.execute("""
                    SELECT count(*) as active_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """)
                conn_count = cursor.fetchone()

                result['status'] = 'healthy'
                result['message'] = 'Database connection is healthy'
                result['details'] = {
                    'database': db_info['current_database'],
                    'user': db_info['current_user'],
                    'version': db_info['version'].split()[0:2],  # PostgreSQL version
                    'active_connections': conn_count['active_connections'],
                    'test_query_result': test_result['test']
                }

        except psycopg2.Error as e:
            result['status'] = 'unhealthy'
            result['message'] = f'Database health check failed: {str(e)}'
            logger.error(f"Health check failed: {e}")

        return result

    def get_schemas(self, exclude_system: bool = True) -> List[str]:
        """Get list of schemas in the database."""
        if not self.connection:
            logger.error("No active connection")
            return []

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if exclude_system:
                    cursor.execute("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
                        ORDER BY schema_name
                    """)
                else:
                    cursor.execute("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        ORDER BY schema_name
                    """)

                schemas = [row['schema_name'] for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(schemas)} schemas")
                return schemas

        except psycopg2.Error as e:
            logger.error(f"Failed to get schemas: {e}")
            return []

    def get_tables(self, schema: str) -> List[Dict[str, Any]]:
        """Get list of tables in a specific schema."""
        if not self.connection:
            logger.error("No active connection")
            return []

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (schema,))

                tables = cursor.fetchall()
                logger.info(f"Retrieved {len(tables)} tables from schema '{schema}'")
                return tables

        except psycopg2.Error as e:
            logger.error(f"Failed to get tables for schema '{schema}': {e}")
            return []

    def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table."""
        if not self.connection:
            logger.error("No active connection")
            return []

        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default,
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (schema, table))

                columns = cursor.fetchall()
                logger.info(f"Retrieved {len(columns)} columns for table '{schema}.{table}'")
                return columns

        except psycopg2.Error as e:
            logger.error(f"Failed to get columns for table '{schema}.{table}': {e}")
            return []

    def get_table_info(self, schema: str, table: str) -> Dict[str, Any]:
        """Get comprehensive information about a table."""
        info = {
            'schema': schema,
            'table': table,
            'columns': self.get_columns(schema, table),
            'row_count': self._get_row_count(schema, table),
            'indexes': self._get_indexes(schema, table),
            'constraints': self._get_constraints(schema, table)
        }
        return info

    def _get_row_count(self, schema: str, table: str) -> Optional[int]:
        """Get approximate row count for a table."""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = sql.SQL("SELECT COUNT(*) as count FROM {}.{}").format(
                    sql.Identifier(schema), sql.Identifier(table)
                )
                cursor.execute(query)
                result = cursor.fetchone()
                return result['count'] if result else None
        except psycopg2.Error as e:
            logger.warning(f"Failed to get row count for {schema}.{table}: {e}")
            return None

    def _get_indexes(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE schemaname = %s AND tablename = %s
                    ORDER BY indexname
                """, (schema, table))

                return cursor.fetchall()
        except psycopg2.Error as e:
            logger.warning(f"Failed to get indexes for {schema}.{table}: {e}")
            return []

    def _get_constraints(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Get constraint information for a table."""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT conname, contype, conkey, confkey
                    FROM pg_constraint
                    WHERE conrelid = (
                        SELECT oid FROM pg_class
                        WHERE relname = %s AND relnamespace = (
                            SELECT oid FROM pg_namespace WHERE nspname = %s
                        )
                    )
                    ORDER BY conname
                """, (table, schema))

                return cursor.fetchall()
        except psycopg2.Error as e:
            logger.warning(f"Failed to get constraints for {schema}.{table}: {e}")
            return []

# Global instance for convenience
db = DatabaseConnection()

# Convenience functions
def connect() -> bool:
    """Connect to database."""
    return db.connect()

def disconnect():
    """Disconnect from database."""
    db.disconnect()

def health_check() -> Dict[str, Any]:
    """Perform health check."""
    return db.health_check()

def get_schemas(exclude_system: bool = True) -> List[str]:
    """Get database schemas."""
    return db.get_schemas(exclude_system)

def get_tables(schema: str) -> List[Dict[str, Any]]:
    """Get tables in schema."""
    return db.get_tables(schema)

def get_columns(schema: str, table: str) -> List[Dict[str, Any]]:
    """Get columns for table."""
    return db.get_columns(schema, table)

def get_table_info(schema: str, table: str) -> Dict[str, Any]:
    """Get comprehensive table information."""
    return db.get_table_info(schema, table)