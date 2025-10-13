# Database Understanding Report

## Overview
Your database is a **PostgreSQL data warehouse** hosted on Supabase, designed for knowledge mining from YouTube transcripts. The system combines traditional relational data warehousing with modern vector search capabilities for AI-powered content analysis.

## Database Configuration
- **Type**: Relational PostgreSQL
- **Host**: Supabase (configured via environment variables)
- **Schema**: `dw` (data warehouse)
- **Architecture**: Star schema with dimension and fact tables
- **Connection**: Managed through `db.py` using psycopg2 connection pooling

## Schema Structure

### Tables Summary
The `dw` schema contains 3 tables with the following row counts:
- `dim_domain`: 4 rows
- `fact_youtube_channels`: 1 row  
- `fact_youtube_transcripts`: 3,962 rows

### Detailed Table Descriptions

#### 1. dim_domain
**Purpose**: Dimension table storing domain information
- **Row Count**: 4
- **Columns**:
  - `id`: bigint(64) NULL
  - `created_at`: timestamp with time zone NULL
  - `domain_name`: text NULL
  - `is_active`: smallint(16) NULL

#### 2. fact_youtube_channels
**Purpose**: Fact table containing YouTube channel metadata
- **Row Count**: 1
- **Columns**:
  - `id`: bigint(64) NULL
  - `created_at`: timestamp with time zone NULL
  - `channel_name`: text NULL
  - `channel_id`: text NULL
  - `channel_url`: text NULL
  - `channel_summary`: text NULL
  - `upload_playlist_id`: text NULL
  - `transcript_sync_active`: bigint(64) NULL

#### 3. fact_youtube_transcripts
**Purpose**: Main fact table storing YouTube video transcripts and metadata
- **Row Count**: 3,962
- **Columns**:
  - `id`: bigint(64) NULL
  - `created_at`: timestamp with time zone NULL
  - `video_url`: character varying NULL
  - `video_id`: character varying NULL
  - `video_name`: text NULL
  - `transcript`: text NULL
  - `video_date`: timestamp with time zone NULL
  - `transcript_length_label`: text NULL
  - `transcript_summary`: jsonb NULL
  - `channel_metadata_id`: bigint(64) NULL
  - `video_domain_id`: bigint(64) NULL
  - `transcript_topics`: ARRAY NULL

## Vector Store Configuration
- **Collection Name**: `hormozi_transcripts`
- **Technology**: PGVector (PostgreSQL extension for vector similarity search)
- **Status**: Not yet created - will be generated dynamically when documents are loaded
- **Expected Structure**:
  - `embedding`: vector(1536) - High-dimensional vectors for similarity search
  - `document`: Text content of transcript chunks
  - `metadata`: JSONB for additional metadata
  - `collection_id`: References the collection

## System Purpose
This database supports a knowledge mining agent focused on YouTube transcripts, likely from Alex Hormozi's content. The system enables:

- **Traditional Analytics**: Structured querying of transcript metadata and channel information
- **AI-Powered Search**: Vector similarity search for semantic content retrieval
- **RAG Capabilities**: Retrieval-Augmented Generation for intelligent content analysis

## Connection Status
✅ Database connection is operational and accessible.

## Recommendations
- Initialize the vector store by loading documents to create the `hormozi_transcripts` collection
- Consider adding indexes on frequently queried columns for performance
- Monitor row growth in `fact_youtube_transcripts` as transcript data accumulates

---
*Report generated based on database inspection and configuration analysis.*