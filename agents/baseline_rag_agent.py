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
    """Baseline RAG agent for business content Q&A.

    Implements a retrieval-augmented generation system using LangChain,
    ChromaDB for vector storage, and OpenAI embeddings. Designed specifically
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
        """Load and index documents into the vector store.

        Args:
            documents: List of LangChain Document objects with content and metadata.
                      Documents should be preprocessed with business-specific chunking.
        """
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=config.get('VECTOR_STORE_PATH', './chroma_db')
        )

    @tool(response_format="content_and_artifact")
    def retrieve_context(self, query: str) -> Tuple[str, List[Document]]:
        """Retrieve relevant business content to help answer a query.

        Performs similarity search against the vector store to find the most
        relevant business advice and frameworks from Alex Hormozi's content.

        Args:
            query: The user's business-related question

        Returns:
            Tuple of (serialized_context, retrieved_documents) where
            serialized_context contains formatted source and content information.
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
        """Initialize the LangChain agent with retrieval tool.

        Creates a zero-shot react agent that can use the retrieval tool
        to gather context before generating responses.
        """
        tools = [self.retrieve_context]

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