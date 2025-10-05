# Chat Interface for Knowledge Mining Agent

A simple web-based chat interface for user acceptance testing of the baseline RAG agent with real Supabase transcript data.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Set up database credentials:**
   ```bash
   python utils/setup_database.py
   ```
   This will prompt you for your Supabase database credentials.

3. **Run the chat interface:**
   ```bash
   python app/app.py
   ```

4. **Open your browser** and go to: http://localhost:5000

## 🎯 Features

- **Clean, responsive chat interface** with modern design
- **Real Supabase transcript data** from your dw schema with:
  - Alex Hormozi YouTube transcripts
  - Enriched summaries and topic modeling
  - Channel metadata
- **Dynamic video citations** - Citations extracted from retrieved chunk metadata
- **Hover thumbnails** - Preview video thumbnails when hovering over citations
- **Direct video links** - Click citations to watch original Alex Hormozi videos
- **Quick suggestion buttons** for common questions
- **Real-time responses** with typing indicators
- **Mobile-friendly** design

## 💬 How to Use

1. **Ask questions** about business topics in the input field
2. **Use suggestion buttons** for quick test questions
3. **Get instant responses** based on business knowledge
4. **Hover over citations** to see video thumbnails
5. **Click citations** to watch the original source videos
6. **Test different scenarios** for user acceptance testing

## 🔧 Technical Details

- **Backend**: Flask web server
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Agent**: Baseline RAG agent with real database integration
- **Database**: Supabase PostgreSQL with dw schema
- **Data**: Real Alex Hormozi transcripts with summaries and topic modeling
- **Styling**: Modern gradient design with responsive layout

## 🗄️ Database Setup

The app connects to your Supabase database and loads transcript data from the `dw` schema. It looks for tables containing "transcript" in the name and expects columns like:

- `transcript` or `content` or `text`: The transcript text
- `video_id` or `youtube_id`: YouTube video identifier
- `title` or `video_title`: Video title
- `summary`: AI-generated summary (if available)
- `topics` or `topic_tags`: Comma-separated topic tags
- `created_at` or `published_at`: Timestamp

If database connection fails, it gracefully falls back to mock data.

## 📊 Current Status

- ✅ Chat interface functional
- ✅ Mock responses working
- ✅ Agent initialization successful
- ✅ Responsive design
- ⚠️ Using mock data (not real vector database)
- ⚠️ Development server (not production-ready)

## 🧪 Testing Scenarios

Try asking questions like:
- "What are the three types of leverage?"
- "How should I approach sales?"
- "What marketing methods work?"
- "How can I scale my business?"

## 🚀 Production Deployment

For production use:

1. **Connect real database** (Supabase with PGVector)
2. **Load actual business content** documents
3. **Use production WSGI server** (Gunicorn, uWSGI) with `app/app.py`
4. **Add authentication** and user management
5. **Implement rate limiting** and security measures

## 🎬 Setting Up Real Video Citations

To use real Alex Hormozi video citations:

### Option 1: Manual Update
1. **Find your video IDs** from YouTube URLs (the part after `v=`)
2. **Update `app.py`** - Replace `your_actual_video_id_1`, `your_actual_video_id_2`, etc. with real IDs
3. **Update video titles** to match your actual content
4. **Test the citations** by hovering and clicking

### Option 2: Use the Update Script (Recommended)
Run the interactive script to update video citations:
```bash
python utils/update_video_ids.py
```

The script will:
- Show current placeholder citations
- Prompt for actual video IDs and titles
- Update the code automatically
- Provide next steps

Example of what gets updated:
```python
# Before:
'video_id': 'your_actual_video_id_1',
'title': '$100M Offers - The Foundation of Business Scaling',

# After:
'video_id': 'ABC123def456',
'title': 'Your Actual Alex Hormozi Video Title',
```

## 🔗 How Citations Work

The citation system simulates real RAG retrieval:

1. **Question Processing**: User asks a business question
2. **Chunk Retrieval**: System simulates retrieving relevant text chunks from vector store
3. **Metadata Extraction**: Each chunk contains video metadata (ID, title, URL, thumbnail)
4. **Citation Generation**: Unique citations are extracted from retrieved chunks
5. **Display**: Citations appear below answers with hover thumbnails and direct links

In production, this will work with real vector search where:
- Chunks are retrieved based on semantic similarity
- Each chunk's metadata includes the source video information
- Citations dynamically reflect which videos were actually referenced

## 📝 Development Notes

- **File Structure**: Chat app in `app/` directory, helper scripts in `utils/`
- The interface uses mock responses for testing
- Real RAG functionality requires database connection
- Agent initializes successfully with OpenAI API key
- Evaluation framework tested and working
- Citations are dynamically generated from chunk metadata
- Ready for integration with real vector store