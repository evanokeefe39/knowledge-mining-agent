"""
Database inspection utilities for Supabase dw schema.

Provides functions to explore and understand the structure of tables
and columns in the dw (data warehouse) schema.
"""

import psycopg2
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config
from log import setup_logger

logger = setup_logger(__name__)


class DatabaseInspector:
    """Utility class for inspecting Supabase database schema and data."""

    def __init__(self):
        """Initialize with database connection parameters."""
        self.user = config.get('SUPABASE__DB_USER')
        self.password = config.get('SUPABASE__DB_PASSWORD')
        self.host = config.get('SUPABASE__DB_HOST')
        self.port = config.get('SUPABASE__DB_PORT', 5432)
        self.dbname = config.get('SUPABASE__DB_NAME')
        self.schema = config.get('database', {}).get('schema', 'dw')

    def _get_connection(self):
        """Get a database connection."""
        if not all([self.user, self.password, self.host, self.dbname]):
            raise ValueError("Missing database connection parameters")

        return psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.dbname
        )

    def list_tables(self) -> List[str]:
        """List all tables in the dw schema.

        Returns:
            List of table names in the dw schema
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """, (self.schema,))

            tables = [row[0] for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            logger.info(f"Found {len(tables)} tables in schema '{self.schema}': {tables}")
            return tables

        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            return []

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed column information for a specific table.

        Args:
            table_name: Name of the table to inspect

        Returns:
            List of dictionaries containing column details
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = %s
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (self.schema, table_name))

            columns = []
            for row in cursor.fetchall():
                column_info = {
                    'name': row[0],
                    'data_type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4],
                    'precision': row[5],
                    'scale': row[6]
                }
                columns.append(column_info)

            cursor.close()
            conn.close()

            logger.info(f"Table '{table_name}' has {len(columns)} columns")
            return columns

        except Exception as e:
            logger.error(f"Error getting columns for table '{table_name}': {str(e)}")
            return []

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a table.

        Args:
            table_name: Name of the table to inspect

        Returns:
            Dictionary containing table metadata and column details
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.{table_name};")
            row_count = cursor.fetchone()[0]

            # Get table size
            cursor.execute("""
                SELECT
                    pg_size_pretty(pg_total_relation_size(%s)) as size
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s;
            """, (f"{self.schema}.{table_name}", self.schema, table_name))

            size_result = cursor.fetchone()
            table_size = size_result[0] if size_result else "Unknown"

            cursor.close()
            conn.close()

            columns = self.get_table_columns(table_name)

            table_info = {
                'name': table_name,
                'schema': self.schema,
                'row_count': row_count,
                'size': table_size,
                'columns': columns
            }

            logger.info(f"Table '{table_name}': {row_count} rows, {len(columns)} columns, size: {table_size}")
            return table_info

        except Exception as e:
            logger.error(f"Error getting info for table '{table_name}': {str(e)}")
            return {}

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from a table.

        Args:
            table_name: Name of the table to sample
            limit: Number of rows to return (default: 5)

        Returns:
            List of dictionaries representing sample rows
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get column names first
            columns = self.get_table_columns(table_name)
            column_names = [col['name'] for col in columns]

            # Get sample data
            cursor.execute(f"SELECT * FROM {self.schema}.{table_name} LIMIT %s;", (limit,))
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            # Convert to list of dicts
            sample_data = []
            for row in rows:
                row_dict = dict(zip(column_names, row))
                sample_data.append(row_dict)

            logger.info(f"Retrieved {len(sample_data)} sample rows from '{table_name}'")
            return sample_data

        except Exception as e:
            logger.error(f"Error getting sample data from '{table_name}': {str(e)}")
            return []

    def get_schema_overview(self) -> Dict[str, Any]:
        """Get a complete overview of the dw schema.

        Returns:
            Dictionary containing all tables and their information
        """
        logger.info(f"Generating schema overview for '{self.schema}'")

        tables = self.list_tables()
        schema_info = {
            'schema': self.schema,
            'tables': {}
        }

        for table_name in tables:
            table_info = self.get_table_info(table_name)
            schema_info['tables'][table_name] = table_info

        logger.info(f"Schema overview complete: {len(tables)} tables analyzed")
        return schema_info

    def print_schema_summary(self):
        """Print a human-readable summary of the schema."""
        schema_info = self.get_schema_overview()

        print(f"\n=== Schema Overview: {schema_info['schema']} ===\n")

        for table_name, table_info in schema_info['tables'].items():
            print(f"📋 Table: {table_name}")
            print(f"   Rows: {table_info.get('row_count', 'Unknown')}")
            print(f"   Size: {table_info.get('size', 'Unknown')}")
            print(f"   Columns: {len(table_info.get('columns', []))}")

            # Show column details
            columns = table_info.get('columns', [])
            if columns:
                print("   Column Details:")
                for col in columns[:5]:  # Show first 5 columns
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"     - {col['name']} ({col['data_type']}) {nullable}")
                if len(columns) > 5:
                    print(f"     ... and {len(columns) - 5} more columns")

            print()

    def find_tables_with_pattern(self, pattern: str) -> List[str]:
        """Find tables whose names match a pattern.

        Args:
            pattern: SQL LIKE pattern (e.g., '%transcript%', 'hormozi_%')

        Returns:
            List of matching table names
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_type = 'BASE TABLE'
                AND table_name LIKE %s
                ORDER BY table_name;
            """, (self.schema, pattern))

            tables = [row[0] for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            logger.info(f"Found {len(tables)} tables matching pattern '{pattern}': {tables}")
            return tables

        except Exception as e:
            logger.error(f"Error finding tables with pattern '{pattern}': {str(e)}")
            return []


def main():
    """Command-line interface for database inspection."""
    import argparse

    parser = argparse.ArgumentParser(description="Inspect Supabase dw schema")
    parser.add_argument("--tables", action="store_true", help="List all tables")
    parser.add_argument("--table", help="Get detailed info for specific table")
    parser.add_argument("--sample", help="Get sample data from specific table")
    parser.add_argument("--pattern", help="Find tables matching pattern")
    parser.add_argument("--overview", action="store_true", help="Print complete schema overview")

    args = parser.parse_args()

    inspector = DatabaseInspector()

    if args.tables:
        tables = inspector.list_tables()
        print("Tables in dw schema:")
        for table in tables:
            print(f"  - {table}")

    elif args.table:
        info = inspector.get_table_info(args.table)
        if info:
            print(f"Table: {info['name']}")
            print(f"Rows: {info['row_count']}")
            print(f"Size: {info['size']}")
            print("Columns:")
            for col in info['columns']:
                print(f"  - {col['name']} ({col['data_type']})")

    elif args.sample:
        sample = inspector.get_sample_data(args.sample)
        if sample:
            print(f"Sample data from {args.sample}:")
            for i, row in enumerate(sample):
                print(f"Row {i+1}: {row}")

    elif args.pattern:
        tables = inspector.find_tables_with_pattern(args.pattern)
        print(f"Tables matching '{args.pattern}':")
        for table in tables:
            print(f"  - {table}")

    elif args.overview:
        inspector.print_schema_summary()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()