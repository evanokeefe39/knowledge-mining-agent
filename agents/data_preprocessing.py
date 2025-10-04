"""
Data preprocessing module for business content.

Handles document chunking, metadata enrichment, and preparation
for vector storage in the RAG system.
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class BusinessContentPreprocessor:
    """Preprocessor for Alex Hormozi's business transcripts."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the preprocessor.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
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
        """Preprocess a single transcript into chunks.

        Args:
            transcript_text: Raw transcript text
            metadata: Metadata including video_id, title, summary, topics, etc.

        Returns:
            List of Document objects ready for vector storage
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
        """Preprocess multiple transcripts.

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