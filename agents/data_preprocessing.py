"""
Data preprocessing module for business content.

Handles document chunking, metadata enrichment, and preparation
for vector storage in the RAG system.
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


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