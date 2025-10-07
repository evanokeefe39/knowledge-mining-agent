"""
Data preprocessing module for business content.

Handles document chunking, metadata enrichment, and preparation
for vector storage in the RAG system.
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import json


class BusinessContentPreprocessor:
    """Preprocessor for Alex Hormozi's business transcripts.

    Handles semantic chunking and metadata enrichment specifically designed
    for business content. Preserves logical coherence of business frameworks
    and advice while preparing documents for vector storage.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the preprocessor with chunking parameters.

        Args:
            chunk_size: Maximum size of each text chunk in characters.
                       Larger chunks preserve more context but may reduce retrieval precision.
            chunk_overlap: Number of characters to overlap between chunks.
                          Helps maintain continuity across business concepts.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def preprocess_transcript(self,
                            transcript_text: str,
                            metadata: Dict[str, Any]) -> List[Document]:
        """Preprocess a single transcript into semantically coherent chunks.

        Splits the transcript text into manageable chunks while preserving
        business-specific context and enriching each chunk with comprehensive metadata.

        Args:
            transcript_text: Raw transcript text from Alex Hormozi's business content
            metadata: Metadata dictionary containing video_id, title, summary,
                     topics, timestamp, and other enrichment data

        Returns:
            List of Document objects ready for vector storage, each containing
            chunked content and enriched metadata for improved retrieval.
        """
        # Split text into chunks
        chunks = self.text_splitter.split_text(transcript_text)

        documents = []
        for i, chunk in enumerate(chunks):
            # Enrich metadata for each chunk
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': i,
                'chunk_start': i * (self.chunk_size - self.chunk_overlap),
                'chunk_end': (i + 1) * (self.chunk_size - self.chunk_overlap) + self.chunk_overlap,
                'total_chunks': len(chunks)
            })

            document = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(document)

        return documents

    def preprocess_batch(self,
                        transcripts: List[Dict[str, Any]]) -> List[Document]:
        """Preprocess multiple transcripts in batch.

        Processes a collection of transcripts, applying consistent chunking
        and metadata enrichment across all business content.

        Args:
            transcripts: List of dictionaries, each containing 'text' (str)
                        and 'metadata' (Dict[str, Any]) keys representing
                        individual business transcripts

        Returns:
            Combined list of all document chunks from all transcripts,
            ready for indexing in the vector store.
        """
        all_documents = []

        for transcript in transcripts:
            docs = self.preprocess_transcript(
                transcript['text'],
                transcript['metadata']
            )
            all_documents.extend(docs)

        return all_documents

    def preprocess_transcript_semantic(self,
                                      transcript_text: str,
                                      metadata: Dict[str, Any]) -> List[Document]:
        """Preprocess a single transcript using semantic chunking with summaries and topics.

        Uses enriched metadata (summaries, topics) to create semantically coherent chunks
        that preserve business content context and maintain video_id relationships.

        Args:
            transcript_text: Raw transcript text from YouTube
            metadata: Metadata dictionary containing video_id, title, summary, topics, etc.

        Returns:
            List of Document objects with semantic chunks and enriched metadata.
        """
        documents = []

        # Extract topics from metadata if available
        topics = metadata.get('topics', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = [t.strip() for t in topics.split(',') if t.strip()]

        summary = metadata.get('summary', metadata.get('transcript_summary', ''))

        # If we have topics, try to split transcript by topic sections
        if topics and len(topics) > 1:
            chunks = self._split_by_topics(transcript_text, topics, summary)
        else:
            # Fallback to enhanced recursive splitting with summary guidance
            chunks = self._split_with_summary_guidance(transcript_text, summary)

        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': i,
                'chunk_type': 'semantic',
                'total_chunks': len(chunks),
                'topics_covered': topics if topics else [],
                'has_summary': bool(summary)
            })

            document = Document(
                page_content=chunk.strip(),
                metadata=chunk_metadata
            )
            documents.append(document)

        return documents

    def _split_by_topics(self, text: str, topics: List[str], summary: str) -> List[str]:
        """Split transcript by topic boundaries for semantic coherence."""
        chunks = []
        remaining_text = text

        for topic in topics:
            # Find topic mentions in text (case insensitive)
            pattern = re.compile(re.escape(topic), re.IGNORECASE)
            matches = list(pattern.finditer(remaining_text))

            if matches:
                # Take text up to the last mention of this topic
                split_point = matches[-1].end()
                chunk = remaining_text[:split_point]
                if len(chunk.strip()) > 50:  # Minimum chunk size
                    chunks.append(chunk)
                remaining_text = remaining_text[split_point:]
            else:
                # If topic not found, continue
                continue

        # Add any remaining text as final chunk
        if remaining_text.strip():
            chunks.append(remaining_text)

        # If no chunks created, fallback to recursive splitting
        if not chunks:
            return self.text_splitter.split_text(text)

        return chunks

    def _split_with_summary_guidance(self, text: str, summary: str) -> List[str]:
        """Split text using summary keywords to guide chunk boundaries."""
        if not summary:
            return self.text_splitter.split_text(text)

        # Extract key phrases from summary (simple approach: split by punctuation)
        key_phrases = re.split(r'[.!?]+', summary)
        key_phrases = [phrase.strip() for phrase in key_phrases if len(phrase.strip()) > 10]

        chunks = []
        remaining_text = text

        for phrase in key_phrases[:3]:  # Limit to first few key phrases
            pattern = re.compile(re.escape(phrase[:50]), re.IGNORECASE)  # First 50 chars
            match = pattern.search(remaining_text)

            if match:
                split_point = match.end()
                chunk = remaining_text[:split_point]
                if len(chunk.strip()) > 100:
                    chunks.append(chunk)
                remaining_text = remaining_text[split_point:]

        # Add remaining text
        if remaining_text.strip():
            chunks.append(remaining_text)

        # Ensure minimum chunk sizes and fallback if needed
        valid_chunks = [c for c in chunks if len(c.strip()) > 50]
        if not valid_chunks:
            return self.text_splitter.split_text(text)

        return valid_chunks

    def preprocess_batch_semantic(self,
                                 transcripts: List[Dict[str, Any]]) -> List[Document]:
        """Preprocess multiple transcripts using semantic chunking.

        Applies semantic chunking to a batch of transcripts, leveraging
        enriched metadata for improved retrieval coherence.

        Args:
            transcripts: List of dictionaries with 'text' and 'metadata' keys

        Returns:
            Combined list of semantic document chunks ready for vector storage.
        """
        all_documents = []

        for transcript in transcripts:
            docs = self.preprocess_transcript_semantic(
                transcript['text'],
                transcript['metadata']
            )
            all_documents.extend(docs)

        return all_documents