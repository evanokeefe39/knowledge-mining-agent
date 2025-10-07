#!/usr/bin/env python3
"""
Vector Store Inspector for Supabase PGVector.

This utility helps inspect the vector store table in Supabase to understand
where the embeddings are stored and their structure.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
import psycopg2
from psycopg2.extras import RealDictCursor


class VectorStoreInspector:
    """Inspector for PGVector tables in Supabase."""

    def __init__(self):
        """Initialize with database connection."""
        self.connection_string = (
            f"postgresql://{config.get('SUPABASE__DB_USER')}:"
            f"{config.get('SUPABASE__DB_PASSWORD')}@"
            f"{config.get('SUPABASE__DB_HOST')}:"
            f"{config.get('SUPABASE__DB_PORT')}/"
            f"{config.get('SUPABASE__DB_NAME')}"
        )
        self.table_name = config.get('VECTOR_STORE_TABLE', 'hormozi_transcripts')
        self.schema = None  # Will be determined when checking table
        self.conn = None

    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            print("Connected to Supabase database")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def check_table_exists(self):
        """Check if the vector store table exists."""
        if not self.conn:
            return False

        try:
            with self.conn.cursor() as cursor:
                # Check in public schema first (PGVector default)
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s AND table_schema = 'public'
                    );
                """, (self.table_name,))
                exists_public = cursor.fetchone()[0]

                # Also check in configured schema
                schema = config.get('database', {}).get('schema', 'public')
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s AND table_schema = %s
                    );
                """, (self.table_name, schema))
                exists_config = cursor.fetchone()[0]

                if exists_public:
                    print(f"Vector store table '{self.table_name}' exists in 'public' schema")
                    self.schema = 'public'
                    return True
                elif exists_config:
                    print(f"Vector store table '{self.table_name}' exists in '{schema}' schema")
                    self.schema = schema
                    return True
                else:
                    print(f"Vector store table '{self.table_name}' does not exist in 'public' or '{schema}' schemas")
                    return False
        except Exception as e:
            print(f"Error checking table: {e}")
            return False

    def get_table_structure(self):
        """Get the structure of the vector store table."""
        if not self.conn or not self.schema:
            return None

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = %s
                    ORDER BY ordinal_position;
                """, (self.table_name, self.schema))
                columns = cursor.fetchall()
                print(f"\nTable Structure for '{self.schema}.{self.table_name}':")
                print("-" * 60)
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"{col['column_name']:20} {col['data_type']:15} {nullable}{default}")
                return columns
        except Exception as e:
            print(f"Error getting table structure: {e}")
            return None

    def get_embedding_count(self):
        """Get the count of embeddings in the table."""
        if not self.conn or not self.schema:
            return 0

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table_name};")
                count = cursor.fetchone()[0]
                print(f"\nTotal embeddings stored: {count}")
                return count
        except Exception as e:
            print(f"Error counting embeddings: {e}")
            return 0

    def sample_embeddings(self, limit=5):
        """Sample some embeddings from the table."""
        if not self.conn or not self.schema:
            return None

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT id, LEFT(document, 100) as document_preview,
                           cmetadata, embedding
                    FROM {self.schema}.{self.table_name}
                    LIMIT %s;
                """, (limit,))
                samples = cursor.fetchall()
                print(f"\nSample Embeddings (first {limit}):")
                print("-" * 60)
                for i, sample in enumerate(samples, 1):
                    print(f"\nSample {i}:")
                    print(f"  ID: {sample['id']}")
                    print(f"  Document: {sample['document_preview']}...")
                    print(f"  Metadata: {sample['cmetadata']}")
                    embedding = sample['embedding']
                    if embedding:
                        print(f"  Embedding: {type(embedding)} with {len(embedding)} dimensions")
                        print(f"    First 5 values: {embedding[:5]}")
                    else:
                        print("  Embedding: None")
                return samples
        except Exception as e:
            print(f"Error sampling embeddings: {e}")
            return None

    def check_pgvector_extension(self):
        """Check if pgvector extension is enabled."""
        if not self.conn:
            return False

        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT name, default_version, installed_version
                    FROM pg_available_extensions
                    WHERE name = 'vector';
                """)
                result = cursor.fetchone()
                if result:
                    name, default_ver, installed_ver = result
                    print(f"pgvector extension: {name} v{installed_ver} (default: v{default_ver})")
                    return True
                else:
                    print("pgvector extension not found")
                    return False
        except Exception as e:
            print(f"Error checking pgvector: {e}")
            return False

    def inspect(self):
        """Run full inspection of the vector store."""
        print("Inspecting Vector Store in Supabase")
        print("=" * 50)

        if not self.connect():
            return

        self.check_pgvector_extension()
        if self.check_table_exists():
            self.get_table_structure()
            self.get_embedding_count()
            self.sample_embeddings()

        self.conn.close()
        print("\nInspection complete")


if __name__ == "__main__":
    inspector = VectorStoreInspector()
    inspector.inspect()