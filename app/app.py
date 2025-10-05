#!/usr/bin/env python3
"""
Simple chat interface for the Baseline RAG Agent.

This Flask application provides a web interface for user acceptance testing
of the baseline RAG agent with mock data.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.baseline_rag_agent import BaselineRAGAgent
from agents.data_preprocessing import BusinessContentPreprocessor
from langchain.schema import Document
from utils.db_inspector import DatabaseInspector

app = Flask(__name__)

# Global agent instance
agent = None
mock_documents = []

def load_real_transcript_data():
    """Load real transcript data from Supabase database."""
    global mock_documents

    try:
        inspector = DatabaseInspector()

        # Use sqlmesh__dw schema as specified
        inspector.schema = 'sqlmesh__dw'
        transcript_table = 'dw__fact_youtube_transcripts__2004009856'
        print(f"[DB] Using transcript table: {transcript_table}")

        # Check if table exists
        try:
            inspector.get_table_columns(transcript_table)
        except Exception as e:
            print(f"[ERROR] Table {transcript_table} not found: {e}")
            print("[ERROR] No transcript table found in dw schema")
            print("Please ensure the transcript data is loaded in the dw schema")
            raise Exception("No transcript data available")
        print(f"[DB] Using transcript table: {transcript_table}")

        # Get table structure
        columns = inspector.get_table_columns(transcript_table)
        print(f"[DB] Table has {len(columns)} columns:")
        for col in columns[:5]:  # Show first 5 columns
            print(f"    - {col['name']} ({col['data_type']})")

        # Load all available data for evaluations (not just sample)
        # First get a sample to understand structure
        sample_data = inspector.get_sample_data(transcript_table, limit=10)
        print(f"[DB] Sample shows {len(sample_data)} rows")

        # Load long form transcripts for better evaluation
        try:
            conn = inspector._get_connection()
            cursor = conn.cursor()

            # Filter for long form transcripts (exclude very short ones)
            # Use transcript_length_label or filter by content length
            cursor.execute(f"""
                SELECT * FROM {inspector.schema}.{transcript_table}
                WHERE (transcript IS NOT NULL AND length(transcript) > 100)
                   OR (transcript_summary IS NOT NULL AND length(transcript_summary::text) > 100)
                   OR length(video_name) > 50  -- Fallback to longer video titles
                ORDER BY
                    CASE
                        WHEN transcript IS NOT NULL THEN length(transcript)
                        ELSE 0
                    END DESC,
                    video_date DESC
                LIMIT 200
            """)
            long_form_rows = cursor.fetchall()

            # Get column names
            columns = inspector.get_table_columns(transcript_table)
            column_names = [col['name'] for col in columns]

            # Convert to dict format
            sample_data = []
            for row in long_form_rows:
                row_dict = dict(zip(column_names, row))
                sample_data.append(row_dict)

            cursor.close()
            conn.close()
            print(f"[DB] Loaded {len(sample_data)} long form transcripts for processing")

        except Exception as e:
            print(f"[WARN] Could not load long form transcripts: {e}, using sample data")
            # Fall back to sample data
            sample_data = inspector.get_sample_data(transcript_table, limit=50)
        print(f"[DB] Retrieved {len(sample_data)} sample transcripts")

        if not sample_data:
            print("[ERROR] No transcript data found in table")
            raise Exception("No transcript data available")

        # Show sample data structure
        if sample_data:
            print("[DB] Sample data structure:")
            sample_row = sample_data[0]
            for key, value in sample_row.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"    {key}: {value[:50]}...")
                else:
                    print(f"    {key}: {value}")

        # Convert database rows to transcript format
        transcripts = []
        for row in sample_data:
            # Try to extract relevant fields - adjust based on actual table structure
            transcript_text = row.get('transcript', row.get('content', row.get('text', '')))

            # If no transcript, try transcript_summary (might contain actual transcript)
            if not transcript_text:
                summary = row.get('transcript_summary')
                if summary:
                    print(f"[DEBUG] Found transcript_summary for row {row.get('id')}: {type(summary)} - {str(summary)[:200]}...")
                    if isinstance(summary, str):
                        try:
                            import json
                            parsed = json.loads(summary)
                            # Check if it's a dict with transcript content
                            if isinstance(parsed, dict):
                                transcript_text = parsed.get('transcript', parsed.get('content', parsed.get('text', str(parsed))))
                            else:
                                transcript_text = str(parsed)
                        except json.JSONDecodeError:
                            transcript_text = summary
                    else:
                        transcript_text = str(summary)

            # For development, use video_name if no transcript data available
            if not transcript_text:
                transcript_text = row.get('video_name', '')
                if transcript_text:
                    print(f"[INFO] Using video title as transcript for development: {row.get('id')}")
                else:
                    print(f"[WARN] Skipping row {row.get('id')} - no content")
                    continue

            # Extract metadata
            metadata = {
                'video_id': row.get('video_id', f'video_{len(transcripts)+1}'),
                'title': row.get('video_name', f'Video {len(transcripts)+1}'),
                'topics': row.get('transcript_topics', []) if row.get('transcript_topics') else [],
                'timestamp': str(row.get('video_date', row.get('created_at', '2024-01-01'))),
                'summary': row.get('transcript_summary', ''),
                'channel': 'Alex Hormozi',
                'url': row.get('video_url', '')
            }

            transcripts.append({
                'text': transcript_text,
                'metadata': metadata
            })

        print(f"[DB] Processed {len(transcripts)} transcripts for chunking")

        if not transcripts:
            print("[ERROR] No valid transcripts found")
            raise Exception("No transcript data available")

        # Process into chunks
        preprocessor = BusinessContentPreprocessor(chunk_size=400, chunk_overlap=100)
        mock_documents = preprocessor.preprocess_batch(transcripts)
        print(f"[DB] Created {len(mock_documents)} document chunks")

        return mock_documents

    except Exception as e:
        print(f"[ERROR] Failed to load real data: {e}")
        import traceback
        traceback.print_exc()
        raise Exception("Failed to load transcript data")

def initialize_mock_data():
    """Fallback mock data when database is unavailable."""
    global mock_documents

    sample_transcripts = [
        {
            'text': """
            The key to scaling a business is understanding leverage. Leverage means using
            other people's time, money, and effort to grow your business. There are three
            main types: capital, people, and code/technology.

            Capital leverage: Using money to buy assets or hire people.
            People leverage: Building a team to execute your vision.
            Code leverage: Creating software that automates tasks 24/7.

            The most scalable is code because it never gets tired and can work at massive scale.
            Focus on building systems that operate without your constant intervention.
            """,
            'metadata': {
                'video_id': 'your_actual_video_id_1',
                'title': '$100M Offers - The Foundation of Business Scaling',
                'topics': ['scaling', 'leverage', 'systems'],
                'timestamp': '2024-01-01'
            }
        },
        {
            'text': """
            Sales is about helping people solve problems, not pushing products. The best
            salespeople listen more than they talk. They ask questions to understand
            customer pain points, then show how their solution creates value.

            People don't buy products - they buy solutions to their problems. Your job
            is to understand their problems deeply and demonstrate how you can make
            their life better. Focus on value creation, not value extraction.

            The sales process: Listen → Understand → Help → Serve.
            """,
            'metadata': {
                'video_id': 'your_actual_video_id_2',
                'title': 'How to Sell Anything to Anyone - Gym Launch Secrets',
                'topics': ['sales', 'listening', 'value'],
                'timestamp': '2024-01-02'
            }
        },
        {
            'text': """
            Marketing should attract, not interrupt. Build systems that bring qualified
            prospects to you instead of chasing them. Content marketing, SEO, and social
            proof are more effective than paid advertising for long-term growth.

            Your marketing should educate and entertain while positioning you as the
            obvious choice. Focus on becoming known for solving specific problems
            in your niche. Consistency beats perfection in marketing.

            The marketing hierarchy: Awareness → Interest → Desire → Action.
            """,
            'metadata': {
                'video_id': 'your_actual_video_id_3',
                'title': 'The Ultimate Marketing Strategy - From $0 to $100M',
                'topics': ['marketing', 'attraction', 'content'],
                'timestamp': '2024-01-03'
            }
        }
    ]

    preprocessor = BusinessContentPreprocessor(chunk_size=400, chunk_overlap=100)
    mock_documents = preprocessor.preprocess_batch(sample_transcripts)
    return mock_documents

def simulate_retrieval(question):
    """Simulate vector store retrieval and extract citations from chunk metadata."""
    question_lower = question.lower()

    # Get all available chunks
    all_chunks = mock_documents

    # Simulate retrieval based on question keywords and content matching
    retrieved_chunks = []

    # Simple keyword-based retrieval simulation
    if any(word in question_lower for word in ['leverage', 'scale', 'scaling']):
        # Find chunks that contain scaling/leverage related content
        retrieved_chunks = [chunk for chunk in all_chunks
                          if any(word in chunk.page_content.lower()
                                for word in ['leverage', 'scale', 'scaling', 'capital', 'people', 'code'])]
    elif any(word in question_lower for word in ['sales', 'sell', 'selling', 'listen']):
        # Find chunks that contain sales related content
        retrieved_chunks = [chunk for chunk in all_chunks
                          if any(word in chunk.page_content.lower()
                                for word in ['sales', 'sell', 'customer', 'listen', 'value'])]
    elif any(word in question_lower for word in ['marketing', 'market', 'advertise']):
        # Find chunks that contain marketing related content
        retrieved_chunks = [chunk for chunk in all_chunks
                          if any(word in chunk.page_content.lower()
                                for word in ['marketing', 'market', 'advertise', 'content', 'seo'])]
    else:
        # Return a diverse set of chunks for general questions
        retrieved_chunks = all_chunks[:min(3, len(all_chunks))]

    # If no chunks found with keyword matching, return some chunks anyway
    if not retrieved_chunks:
        retrieved_chunks = all_chunks[:min(2, len(all_chunks))]

    # Extract unique citations from retrieved chunks
    citations = []
    seen_video_ids = set()

    for chunk in retrieved_chunks:
        video_id = chunk.metadata.get('video_id')
        if video_id and video_id not in seen_video_ids and not video_id.startswith('your_actual'):
            citations.append({
                'video_id': video_id,
                'title': chunk.metadata.get('title', 'Unknown Video'),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'slug': chunk.metadata.get('title', '').lower().replace(' ', '-').replace('[^a-z0-9-]', '')[:50]
            })
            seen_video_ids.add(video_id)

    # If no real citations found, provide a fallback
    if not citations:
        # Use the first available chunk's metadata as fallback
        if all_chunks:
            chunk = all_chunks[0]
            video_id = chunk.metadata.get('video_id', 'sample_video')
            citations = [{
                'video_id': video_id,
                'title': chunk.metadata.get('title', 'Business Content'),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'slug': 'business-content'
            }]

    return citations

def get_mock_answer(question):
    """Get a mock answer with citations based on simulated vector retrieval."""
    question_lower = question.lower()

    # Simulate retrieval and get citations from chunk metadata
    citations = simulate_retrieval(question)

    if any(word in question_lower for word in ['leverage', 'scale', 'scaling']):
        return {
            'answer': """The three main types of leverage in business are:

1. **Capital Leverage**: Using money to buy assets or hire people that work for you
2. **People Leverage**: Building a team to execute your vision and handle operations
3. **Code/Technology Leverage**: Creating software and systems that automate tasks and scale infinitely

The most powerful leverage is code/technology because it can work 24/7 without getting tired, making mistakes, or requiring sleep. Focus on building systems that operate without your constant intervention.""",
            'citations': citations
        }

    elif any(word in question_lower for word in ['sales', 'sell', 'selling', 'listen']):
        return {
            'answer': """Great salespeople listen more than they talk. The key principles are:

1. **Listen First**: Ask questions to understand customer problems deeply
2. **Help, Don't Sell**: Focus on solving problems rather than pushing products
3. **Create Value**: Show how your solution genuinely improves their life
4. **Serve Long-term**: Build relationships, not just transactions

Remember: People don't buy products, they buy solutions to their problems. Your role is to be a helpful guide, not a pushy salesperson.""",
            'citations': citations
        }

    elif any(word in question_lower for word in ['marketing', 'market', 'advertise']):
        return {
            'answer': """Effective marketing attracts rather than interrupts:

1. **Content Marketing**: Create valuable content that educates and entertains
2. **SEO & Visibility**: Become findable for people searching for solutions
3. **Social Proof**: Let satisfied customers do your marketing for you
4. **Consistency**: Regular, imperfect action beats sporadic perfection

Focus on becoming known as the go-to expert for solving specific problems in your niche. Build systems that bring qualified prospects to you automatically.""",
            'citations': citations
        }

    else:
        return {
            'answer': """I'd be happy to help with your business question! Based on Alex Hormozi's principles, the key to business success involves:

- **Leverage**: Use systems, teams, and technology to scale beyond your personal limitations
- **Value Creation**: Focus on genuinely helping customers solve their problems
- **Systems Thinking**: Build processes that work without your constant intervention

Could you ask a more specific question about scaling, sales, marketing, or business systems?""",
            'citations': citations
        }

@app.route('/')
def home():
    """Serve the chat interface."""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get response from agent (using mock for now)
        result = get_mock_answer(user_message)

        return jsonify({
            'response': result['answer'],
            'citations': result['citations'],
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'agent_initialized': agent is not None,
        'mock_documents': len(mock_documents) if mock_documents else 0
    })

if __name__ == '__main__':
    # Initialize data (try real database first, fallback to mock)
    print("Loading transcript data...")
    mock_documents = load_real_transcript_data()
    print(f"Loaded {len(mock_documents)} document chunks")

    # Initialize agent (optional, for future real implementation)
    try:
        print("Initializing RAG agent...")
        agent = BaselineRAGAgent()
        agent.initialize_agent()
        print("Agent initialized successfully")
    except Exception as e:
        print(f"Agent initialization failed (expected without real DB): {e}")
        print("Continuing with mock responses...")

    # Start the server
    print("Starting chat interface on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)