# Project Journal

This file records pivots, architecture decisions, major challenges, and other notes of record as the project evolves.

## Initial Setup (2024)
- Created project structure with Poetry for dependency management
- Added core dependencies: LangChain, YouTube transcripts, Google API, PostgreSQL
- Established basic agent skeleton with tools and configuration

## Database Integration (2024)
- Implemented health check for Supabase PostgreSQL connection
- Focused on querying existing enriched data in dw schema
- Removed API ingestion requirements to focus on analysis

## RAG Implementation (2025)
- Renamed /agent to /agents to support multiple implementations
- Implemented baseline RAG system using LangChain and ChromaDB
- Added semantic chunking for business content preprocessing
- Integrated RAGAS evaluation framework
- Updated configuration management with dynamic expansion and secret obfuscation

## Architecture Decisions
- **RAG Choice**: Selected retrieval-augmented generation over naive approaches for better context handling in business content
- **Vector Store**: ChromaDB for simplicity and local development, with Pinecone as production option
- **Chunking**: Semantic chunking over fixed-size to preserve business framework coherence
- **Evaluation**: RAGAS framework for comprehensive metrics (precision, recall, faithfulness, relevancy)

## Challenges
- Balancing semantic chunking with retrieval precision for business content
- Managing configuration across multiple services (OpenAI, Supabase, vector stores)
- Ensuring evaluation metrics align with business domain requirements

## Pivots
- Shifted from API ingestion to focus on analysis of existing enriched data
- Adopted multi-agent architecture to support experimentation
- Prioritized evaluation framework for iterative improvement

## Future Considerations
- Implement production vector store (Pinecone)
- Add synthetic data generation for evaluation
- Explore fine-tuning for domain-specific performance
- Consider A/B testing framework for RAG configurations