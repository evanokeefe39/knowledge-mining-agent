# Project Specifications

## Overview
This project implements a knowledge mining agent focused on Alex Hormozi's business content. The system uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers to business-related questions.

## Functional Requirements
- Implement baseline RAG system using LangChain with ChromaDB vector storage
- Preprocess business transcripts with semantic chunking and metadata enrichment
- Provide retrieval tool for context-aware Q&A
- Support evaluation using RAGAS framework (context precision, recall, faithfulness, relevancy)
- Query and analyze enriched data from Supabase PostgreSQL database under the dw schema
- Use LangChain for agent orchestration and tool management
- Provide health check for database connectivity
- Support configuration via environment variables and config.yaml

## Non-Functional Requirements
- Ensure scalability for large-scale data processing and LLM enrichment
- Optimize for cost-effective API usage and hosting
- Follow PEP8 coding standards
- Maintain security by using environment variables for sensitive data
- Support multiple agent implementations for experimentation

## Architecture
- `/agents` directory contains different agent implementations
- Baseline RAG agent with retrieval tool and LangChain agent
- Data preprocessing with semantic chunking for business content
- Evaluation framework using RAGAS metrics
- Configuration management via config.py parsing YAML and .env