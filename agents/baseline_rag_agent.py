"""
Baseline RAG Agent for Alex Hormozi's business content.

This module implements a basic Retrieval-Augmented Generation (RAG) system
using LangChain, pgvector in Supabase for vector storage, and OpenAI embeddings.
"""

import os
from typing import List, Tuple

from langchain.tools import tool
from langchain.agents import Tool
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class BaselineRAGAgent:
    """Baseline RAG agent for business content Q&A.

    Implements a retrieval-augmented generation system using LangChain,
    pgvector in Supabase for vector storage, and OpenAI embeddings. Designed specifically
    for Alex Hormozi's business content with agentic retrieval capabilities.
    """

    def __init__(self):
        """Initialize the RAG agent with vector store and tools.

        Sets up OpenAI embeddings and prepares the agent for document loading.
        """
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.get('OPENAI_API_KEY')
        )
        self.vector_store = None
        self.agent = None

    def load_documents(self, documents: List[Document]):
        """Load and index documents into the Supabase PGVector store.

        Args:
            documents: List of LangChain Document objects with content and metadata.
                      Documents should be preprocessed with business-specific chunking.
        """
        # Build connection string for Supabase
        schema = config.get('database', {}).get('schema', 'dw')
        connection_string = (
            f"postgresql://{config.get('SUPABASE__DB_USER')}:"
            f"{config.get('SUPABASE__DB_PASSWORD')}@"
            f"{config.get('SUPABASE__DB_HOST')}:"
            f"{config.get('SUPABASE__DB_PORT')}/"
            f"{config.get('SUPABASE__DB_NAME')}"
        )

        self.vector_store = PGVector.from_documents(
            documents=documents,
            embedding=self.embeddings,
            connection_string=connection_string,
            collection_name=config.get('VECTOR_STORE_TABLE', 'hormozi_transcripts')
        )

    def _retrieve_context(self, query: str) -> str:
        """Retrieve relevant business content to help answer a query.

        Performs similarity search against the vector store to find the most
        relevant business advice and frameworks from Alex Hormozi's content.

        Args:
            query: The user's business-related question

        Returns:
            Formatted string containing relevant context from documents.
        """
        if not self.vector_store:
            return "No documents loaded in vector store."

        retrieved_docs = self.vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized

    def initialize_agent(self):
        """Initialize the LangChain agent with retrieval tool.

        Creates a zero-shot react agent that can use the retrieval tool
        to gather context before generating responses.
        """
        tools = [
            Tool(
                name="retrieve_context",
                func=self._retrieve_context,
                description="Retrieve relevant business content to help answer a query. Use this tool to find business advice and frameworks from Alex Hormozi's content."
            )
        ]

        llm = OpenAI(
            temperature=config.get('AGENT__TEMPERATURE', 0.0),
            openai_api_key=config.get('OPENAI_API_KEY')
        )

        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=config.get('AGENT__VERBOSE', True)
        )

    def query(self, question: str) -> str:
        """Answer a business question using the RAG system.

        Args:
            question: The user's business-related question about entrepreneurship,
                     sales, marketing, or scaling strategies.

        Returns:
            The agent's response with relevant business advice and context.

        Raises:
            ValueError: If the agent has not been initialized.
        """
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")

        return self.agent.run(question)