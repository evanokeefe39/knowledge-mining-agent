"""
Data preprocessing module for business content.

Handles document chunking, metadata enrichment, and preparation
for vector storage in the RAG system.
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
try:
    from langchain_experimental.text_splitter import SemanticChunker
    SEMANTIC_CHUNKER_AVAILABLE = True
except ImportError:
    SEMANTIC_CHUNKER_AVAILABLE = False
from langchain_openai import OpenAIEmbeddings
import re
import json
import tiktoken
import nltk
from nltk.corpus import stopwords
import os


class BusinessContentPreprocessor:
    """Preprocessor for YouTube transcripts with adaptive chunking.

    Implements the chunking strategy from specs: recursive token-based splitting,
    semantic refinement, and optional hierarchy mapping for RAG applications.
    """

    def __init__(self,
                 max_chunk_size: int = 400,
                 min_chunk_size: int = 150,
                 chunk_overlap: int = 50,
                 use_semantic_refinement: bool = True,
                 use_hierarchy: bool = False,
                 stopwords_path: str = None):
        """Initialize the preprocessor with chunking parameters.

        Args:
            max_chunk_size: Maximum tokens per chunk (default: 400)
            min_chunk_size: Minimum tokens per chunk (default: 150)
            chunk_overlap: Tokens to overlap between chunks (default: 50)
            use_semantic_refinement: Whether to apply semantic chunking after recursive
            use_hierarchy: Whether to create parent-child chunk relationships
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_semantic_refinement = use_semantic_refinement
        self.use_hierarchy = use_hierarchy

        # Initialize token counter
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding

        # Recursive splitter for initial chunking
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._tokens_to_chars(max_chunk_size),
            chunk_overlap=self._tokens_to_chars(chunk_overlap),
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=self._count_tokens
        )

        # Semantic chunker for refinement
        if use_semantic_refinement and SEMANTIC_CHUNKER_AVAILABLE:
            self.semantic_chunker = SemanticChunker(
                OpenAIEmbeddings(),
                breakpoint_threshold_type="percentile"
            )
        else:
            self.semantic_chunker = None

        # For hierarchy: parent chunk size
        self.parent_chunk_size = 2000  # tokens
        self.parent_splitter = TokenTextSplitter(
            chunk_size=self.parent_chunk_size,
            chunk_overlap=chunk_overlap
        )

    def _tokens_to_chars(self, tokens: int) -> int:
        """Estimate character count from token count (rough approximation)."""
        # Average ~4 chars per token for English text
        return tokens * 4

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))

    def _preprocess_text(self, text: str) -> str:
        """Preprocess transcript text as per spec."""
        # Remove non-content artifacts
        text = re.sub(r'[^\w\s.,!?-]', '', text)  # Remove special symbols except basic punctuation

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove repeated utterances (simple pattern: 3+ identical words)
        text = re.sub(r'\b(\w+)\s+\1\s+\1+\b', r'\1', text)

        # Optionally strip YouTube intro/outro (simple heuristic)
        # Remove common intro patterns
        intro_patterns = [
            r'^(welcome back|hey everyone|what\'s up|hello everyone).*?(?=[\.!?])',
            r'^(today.*?(?=we\'re going to|I\'m going to|let\'s talk about))'
        ]
        for pattern in intro_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

        # Remove outro patterns
        outro_patterns = [
            r'(thanks for watching|subscribe|like and subscribe|see you next time).*$'
        ]
        for pattern in outro_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

        return text.strip()

    def _ensure_chunk_sizes(self, chunks: List[str], depth: int = 0) -> List[str]:
        """Ensure chunks meet min/max token requirements."""
        if depth > 10:  # Prevent infinite recursion
            return chunks

        valid_chunks = []
        for chunk in chunks:
            token_count = self._count_tokens(chunk)
            if token_count >= self.min_chunk_size:
                if token_count > self.max_chunk_size:
                    # Split oversized chunks
                    sub_chunks = self.recursive_splitter.split_text(chunk)
                    if len(sub_chunks) == 1 and sub_chunks[0] == chunk:
                        # Splitter couldn't split, force split by character
                        mid = len(chunk) // 2
                        sub_chunks = [chunk[:mid], chunk[mid:]]
                    valid_chunks.extend(self._ensure_chunk_sizes(sub_chunks, depth + 1))
                else:
                    valid_chunks.append(chunk)
            # Note: chunks smaller than min_chunk_size are discarded
        return valid_chunks

    def preprocess_transcript(self,
                             transcript_text: str,
                             metadata: Dict[str, Any]) -> List[Document]:
        """Preprocess a single transcript using adaptive chunking strategy.

        Implements recursive token-based splitting with optional semantic refinement
        and hierarchy mapping as specified.

        Args:
            transcript_text: Raw transcript text
            metadata: Metadata dictionary with video_id, title, etc.

        Returns:
            List of Document objects with chunked content and metadata
        """
        # Step 0: Preprocessing
        transcript_text = self._preprocess_text(transcript_text)

        # Step 1: Recursive splitting
        initial_chunks = self.recursive_splitter.split_text(transcript_text)

        # Step 2: Ensure chunk size constraints
        chunks = self._ensure_chunk_sizes(initial_chunks)

        # Step 3: Optional semantic refinement
        if self.use_semantic_refinement and self.semantic_chunker and len(chunks) > 1:
            try:
                # Combine chunks for semantic analysis
                combined_text = "\n\n".join(chunks)
                semantic_chunks = self.semantic_chunker.split_text(combined_text)
                # Re-ensure sizes after semantic splitting
                chunks = self._ensure_chunk_sizes(semantic_chunks)
            except Exception as e:
                # Fallback to initial chunks if semantic fails
                print(f"Semantic chunking failed, using recursive chunks: {e}")

        # Step 4: Create parent chunks if hierarchy enabled
        parent_chunks = []
        if self.use_hierarchy:
            parent_texts = self.parent_splitter.split_text(transcript_text)
            for i, parent_text in enumerate(parent_texts):
                parent_chunks.append({
                    'id': f"parent_{i}",
                    'content': parent_text,
                    'child_indices': []  # Will be populated below
                })

        # Step 5: Create documents with hierarchy mapping
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': f"child_{i}",
                'chunk_index': i,
                'total_chunks': len(chunks),
                'token_count': self._count_tokens(chunk),
                'chunk_type': 'semantic' if self.use_semantic_refinement else 'recursive'
            })

            # Map to parent chunk if hierarchy enabled
            if self.use_hierarchy and parent_chunks:
                # Simple mapping: assign to parent containing most of the chunk
                parent_index = min(i // 2, len(parent_chunks) - 1)  # Rough mapping
                chunk_metadata['parent_id'] = parent_chunks[parent_index]['id']
                parent_chunks[parent_index]['child_indices'].append(i)

            document = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(document)

        # Add parent documents if hierarchy enabled
        if self.use_hierarchy:
            for parent in parent_chunks:
                parent_metadata = metadata.copy()
                parent_metadata.update({
                    'chunk_id': parent['id'],
                    'chunk_type': 'parent',
                    'child_indices': parent['child_indices'],
                    'token_count': self._count_tokens(parent['content'])
                })
                parent_doc = Document(
                    page_content=parent['content'],
                    metadata=parent_metadata
                )
                documents.append(parent_doc)

        return documents

    def preprocess_batch(self,
                         transcripts: List[Dict[str, Any]]) -> List[Document]:
        """Preprocess multiple transcripts in batch with adaptive chunking.

        Args:
            transcripts: List of dicts with 'text' and 'metadata' keys

        Returns:
            Combined list of all document chunks
        """
        all_documents = []

        for transcript in transcripts:
            docs = self.preprocess_transcript(
                transcript['text'],
                transcript['metadata']
            )
            all_documents.extend(docs)

        return all_documents

    # Legacy methods for backward compatibility
    def preprocess_transcript_semantic(self,
                                       transcript_text: str,
                                       metadata: Dict[str, Any]) -> List[Document]:
        """Legacy semantic preprocessing - now uses main preprocess_transcript."""
        return self.preprocess_transcript(transcript_text, metadata)

    def preprocess_batch_semantic(self,
                                  transcripts: List[Dict[str, Any]]) -> List[Document]:
        """Legacy batch semantic preprocessing."""
        return self.preprocess_batch(transcripts)

    # Legacy methods for backward compatibility
    def preprocess_transcript_semantic(self,
                                       transcript_text: str,
                                       metadata: Dict[str, Any]) -> List[Document]:
        """Legacy semantic preprocessing - now uses main preprocess_transcript."""
        return self.preprocess_transcript(transcript_text, metadata)

    def preprocess_batch_semantic(self,
                                  transcripts: List[Dict[str, Any]]) -> List[Document]:
        """Legacy batch semantic preprocessing."""
        return self.preprocess_batch(transcripts)