#!/usr/bin/env python3
"""
Create vector embeddings for YouTube transcripts using semantic chunking.

This script fetches enriched YouTube transcript data from Supabase,
applies semantic chunking using summaries and topics, and creates
vector embeddings for RAG retrieval.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from agents.baseline_rag_agent import BaselineRAGAgent
from agents.data_preprocessing import BusinessContentPreprocessor
from config import config
import psycopg2
from psycopg2.extras import RealDictCursor


def fetch_youtube_transcripts(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch enriched YouTube transcript data from Supabase.

    Args:
        limit: Maximum number of transcripts to fetch

    Returns:
        List of transcript dictionaries with metadata
    """
    connection_string = (
        f"postgresql://{config.get('SUPABASE__DB_USER')}:"
        f"{config.get('SUPABASE__DB_PASSWORD')}@"
        f"{config.get('SUPABASE__DB_HOST')}:"
        f"{config.get('SUPABASE__DB_PORT')}/"
        f"{config.get('SUPABASE__DB_NAME')}"
    )

    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch transcripts with summaries
    cursor.execute(f"""
        SELECT video_id, video_name, video_url, transcript, transcript_summary, video_date
        FROM {config.get('database', {}).get('schema', 'dw')}.fact_youtube_transcripts
        WHERE (transcript IS NOT NULL AND length(transcript) > 200)
           OR (transcript_summary IS NOT NULL AND length(transcript_summary::text) > 100)
        ORDER BY video_date DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    transcripts = []
    for row in rows:
        # Use transcript if available, otherwise try to extract from summary
        transcript_text = row.get('transcript')
        if not transcript_text and row.get('transcript_summary'):
            # If summary is JSON, try to extract content
            summary = row['transcript_summary']
            if isinstance(summary, str):
                try:
                    import json
                    parsed = json.loads(summary)
                    transcript_text = parsed.get('transcript', parsed.get('content', str(parsed)))
                except:
                    transcript_text = str(summary)

        if transcript_text and len(transcript_text) > 100:
            metadata = {
                'video_id': row.get('video_id', ''),
                'title': row.get('video_name', ''),
                'url': row.get('video_url', ''),
                'timestamp': str(row.get('video_date', '')),
                'summary': row.get('transcript_summary', ''),
                'transcript_summary': row.get('transcript_summary', ''),
                'channel': 'Alex Hormozi',
                'source': 'youtube_transcript'
            }
            transcripts.append({
                'text': transcript_text,
                'metadata': metadata
            })

    return transcripts


def create_embeddings_pipeline():
    """Create vector embeddings for YouTube transcripts with semantic chunking."""
    print("Creating vector embeddings for YouTube transcripts")
    print("=" * 60)

    # Fetch transcript data
    print("Fetching YouTube transcript data from Supabase...")
    transcripts = fetch_youtube_transcripts(limit=20)
    print(f"Found {len(transcripts)} transcripts with sufficient content")

    if not transcripts:
        print("No suitable transcripts found")
        return

    # Initialize preprocessor with semantic chunking
    print("Applying semantic chunking...")
    preprocessor = BusinessContentPreprocessor(chunk_size=800, chunk_overlap=100)
    documents = preprocessor.preprocess_batch_semantic(transcripts)

    print(f"Created {len(documents)} semantic chunks from {len(transcripts)} transcripts")

    # Initialize RAG agent and load documents
    print("Creating vector embeddings...")
    rag_agent = BaselineRAGAgent()
    rag_agent.load_documents(documents)

    print("Vector embeddings created and stored in Supabase PGVector")
    print(f"Total chunks indexed: {len(documents)}")

    # Test retrieval
    print("\nTesting retrieval with sample query...")
    test_query = "What does Alex Hormozi say about scaling businesses?"
    try:
        context = rag_agent._retrieve_context(test_query)
        print(f"Retrieved context preview: {context[:300]}...")
    except Exception as e:
        print(f"Retrieval test failed: {e}")

    print("\nYouTube transcript embeddings pipeline complete!")
    print("You can now use the RAG agent to query business content with improved semantic retrieval.")


if __name__ == "__main__":
    create_embeddings_pipeline()