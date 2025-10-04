# Knowledge Mining Agent

## Background
This project aims to build an AI-powered knowledge mining agent using LangChain. The agent processes and extracts insights from various sources such as YouTube transcripts and Google APIs, storing structured data in a PostgreSQL database for querying and analysis.

### Goals
- Develop an agent capable of mining knowledge from multimedia and text sources.
- Integrate with external APIs for data retrieval.
- Ensure scalable data storage and retrieval.

### Challenges
- Handling diverse data formats from APIs.
- Optimizing for large-scale data processing and LLM enrichment.
- Managing costs for API usage and hosting.

## Journal
- **Initial Setup**: Created project structure with Poetry, added dependencies for LangChain, YouTube transcripts, Google API, and PostgreSQL.
- **Agent Skeleton**: Implemented basic LangChain agent structure with tools and configuration.
- **Database Integration**: Added health check for Supabase PostgreSQL connection.
- **Spec Update**: Adjusted functional requirements to focus on querying existing enriched data in Supabase dw schema, removing need for API ingestion.
- **RAG Implementation**: Implemented baseline RAG system with pgvector in Supabase, semantic chunking, and RAGAS evaluation framework.
- **Database Utilities**: Created `utils/db_inspector.py` for exploring dw schema structure and understanding data organization.

## Benchmarks for Project
TODO: see what benchmarks are appropriate for this data and application

## Architecture
TODO: justify architecture choices i.e VM sizes, API usage, self hosted services etc 

## Costs
TODO: deomonstrate cost estimation for vectorizing + enriching w/ LLM + indexing in search services etc.

TODO: hosting costs and expecteded token consumption

# Custom Evals

# Fine tuning

# Processing Methods




