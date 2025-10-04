# Agent Development Guidelines - Knowledge Mining Agent

This document contains project-specific guidelines for developing agents in the Knowledge Mining Agent project.

## Core Principles

### Business Content Focus
- All agents must be designed for Alex Hormozi's business content
- Prioritize actionable business advice over generic responses
- Maintain context of entrepreneurship, sales, marketing, and scaling frameworks
- Ensure responses are practical and implementation-focused

### RAG-First Architecture
- Always use Retrieval-Augmented Generation as the foundation
- Retrieval should happen before generation for factual accuracy
- Use pgvector in Supabase for all vector storage operations
- Implement proper chunking strategies for business content coherence

## Agent Types

### Baseline RAG Agent (`agents/baseline_rag_agent.py`)
- **Purpose**: Core Q&A functionality for business content
- **Components**:
  - Supabase pgvector store with OpenAI embeddings
  - LangChain agent with retrieval tool
  - Semantic chunking for business transcripts
- **Evaluation**: Use RAGAS metrics (precision, recall, faithfulness, relevancy)

### Future Agent Types
- **Multi-turn Agent**: Handle follow-up questions with conversation memory
- **Comparative Agent**: Compare different business strategies across transcripts
- **Framework Agent**: Extract and explain specific business frameworks
- **Recommendation Agent**: Provide personalized business advice based on user context

## Development Standards

### Configuration
- Use namespaced environment variables: `SERVICE__SETTING`
- Store secrets in `.env`, non-secrets in `config.yaml`
- Use dynamic expansion: `${VAR_NAME}` in YAML configs
- Obfuscate secrets in logs using `config.get_obfuscated()`

### Database Integration
- All vector operations use Supabase pgvector
- Connection string format: `postgresql://user:pass@host:port/db`
- Table naming: `hormozi_transcripts` for main content
- Health checks must verify pgvector extension availability (see `utils/health_check.py`)

### Code Quality
- Comprehensive docstrings for all public methods
- Type hints for function parameters and returns
- Follow PEP8 with 88-character line limits
- Use the custom logger from `log.py` for all logging

### Testing & Evaluation
- Implement RAGAS evaluation for all agent responses
- Track context precision, recall, faithfulness, and relevancy
- Use synthetic data generation for evaluation datasets
- Maintain evaluation baselines for performance tracking

## Database Integration
- Use `utils/db_inspector.py` to explore dw schema structure
- Validate table names and column schemas before agent development
- Check data types and relationships for proper data preprocessing
- Use sample data to understand content structure for chunking strategies

## Implementation Checklist

### For New Agents
- [ ] Create agent class in `agents/` directory
- [ ] Implement proper initialization with config
- [ ] Add vector store integration (pgvector)
- [ ] Include retrieval tools for context gathering
- [ ] Add comprehensive docstrings
- [ ] Update health checks if new services added
- [ ] Add evaluation integration
- [ ] Update AGENTS.md with new agent details

### For Agent Improvements
- [ ] Run existing evaluation suite
- [ ] Document performance improvements
- [ ] Update configuration if needed
- [ ] Maintain backward compatibility
- [ ] Update journal with changes

## Architecture Decisions
- **RAG System**: Chose retrieval-augmented generation for business content analysis
- **Vector Store**: pgvector in Supabase for both development and production
- **Chunking**: Semantic chunking to preserve business framework coherence
- **Evaluation**: RAGAS framework for comprehensive metrics

## Performance Targets

### RAG Metrics Baseline
- Context Precision: > 0.85
- Context Recall: > 0.80
- Faithfulness: > 0.90
- Answer Relevancy: > 0.85

### Response Quality
- Business-focused answers
- Actionable recommendations
- Proper citation of source content
- Consistent with Hormozi's frameworks

## Deployment Considerations

### Supabase Integration
- Use connection pooling for production
- Implement proper error handling for database operations
- Monitor vector search performance
- Plan for data backup and migration strategies

### API Management
- Implement rate limiting for OpenAI calls
- Cache frequent queries when appropriate
- Monitor token usage and costs
- Handle API failures gracefully

### Scalability
- Design for multiple concurrent users
- Implement async operations where beneficial
- Monitor memory usage for large document sets
- Plan for horizontal scaling if needed

## Research Integration

### From RESEARCH.md
- Follow RAGAS evaluation framework
- Implement semantic chunking strategies
- Use agentic retrieval patterns
- Focus on business domain evaluation

### Experimentation Guidelines
- Create feature branches for experimental agents
- Document experiment results in JOURNAL.md
- Use evaluation metrics to compare approaches
- Archive unsuccessful experiments appropriately

## Maintenance

### Regular Tasks
- Update dependencies quarterly
- Review and update evaluation baselines
- Monitor production performance metrics
- Refresh vector embeddings as content grows

### Documentation Updates
- Keep AGENTS_PROJECT.md current with new agents
- Update JOURNAL.md with significant changes
- Maintain accurate SPEC.md requirements
- Update README.md with new features