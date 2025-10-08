#!/usr/bin/env python3
"""
Test script for db.py module and schema inspection.
"""

import logging
import tempfile
import db
from config import config

# Set up logging to temp file
temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(temp_log.name),
        logging.StreamHandler()  # Also to console
    ]
)

print(f"Logging to temp file: {temp_log.name}")

def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"Connection successful: {result}")
        db.close_db(conn)
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def describe_schema():
    """Describe the database schema."""
    schema = config.database.schema
    print(f"\nDescribing {schema} schema...")
    try:
        conn = db.get_db()
        cursor = conn.cursor()

        # Get all tables in dw schema
        schema = config.database.schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
        """, (schema,))
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in dw schema")
            db.close_db(conn)
            return

        print(f"Found {len(tables)} tables in {schema} schema:")
        for (table_name,) in tables:
            print(f"\nTable: {table_name}")

            # Get columns
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table_name))
            columns = cursor.fetchall()

            print("  Columns:")
            for col_name, data_type, nullable, default in columns:
                null_str = "NULL" if nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"    {col_name}: {data_type} {null_str}{default_str}")

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}")
                count = cursor.fetchone()[0]
                print(f"  Row count: {count}")
            except Exception as e:
                print(f"  Row count: Error - {e}")

        db.close_db(conn)

    except Exception as e:
        print(f"Schema inspection failed: {e}")

if __name__ == "__main__":
    if test_connection():
        describe_schema()
    else:
        print("Cannot proceed with schema inspection due to connection failure")

    print(f"\nLog file saved to: {temp_log.name}")
    temp_log.close()  # Close but don't delete