"""
Baseline RAG Agent for Alex Hormozi's business content.

This module implements a basic Retrieval-Augmented Generation (RAG) system
using LangChain, ChromaDB for vector storage, and OpenAI embeddings.
"""

import os
from typing import List, Tuple

from langchain.tools import tool
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

from ..config import config


class BaselineRAGAgent:
    """Baseline RAG agent for business content Q&A."""

    def __init__(self):
        """Initialize the RAG agent with vector store and tools."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.get('OPENAI_API_KEY')
        )
        self.vector_store = None
        self.agent = None

    def load_documents(self, documents: List[Document]):
        """Load and index documents into the vector store.

        Args:
            documents: List of LangChain Document objects with content and metadata
        """
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=config.get('VECTOR_STORE_PATH', './chroma_db')
        )

    @tool(response_format="content_and_artifact")
    def retrieve_context(self, query: str) -> Tuple[str, List[Document]]:
        """Retrieve information to help answer a query.

        Args:
            query: The user's question

        Returns:
            Tuple of (serialized_context, retrieved_documents)
        """
        if not self.vector_store:
            return "No documents loaded in vector store.", []

        retrieved_docs = self.vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    def initialize_agent(self):
        """Initialize the LangChain agent with retrieval tool."""
        tools = [self.retrieve_context]

        llm = OpenAI(
            temperature=0,
            openai_api_key=config.get('OPENAI_API_KEY')
        )

        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def query(self, question: str) -> str:
        """Answer a question using the RAG system.

        Args:
            question: The user's question

        Returns:
            The agent's response
        """
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")

        return self.agent.run(question)