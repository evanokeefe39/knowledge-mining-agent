# Chunking and Retrieval Strategy Specification

## Objective

Implement a robust and adaptive chunking and retrieval pipeline for long, variable-density YouTube transcripts (up to ~60,000 tokens) without timestamps or structural metadata. The pipeline should maximize semantic coherence and retrieval accuracy for RAG-based applications.

---

## Chunking Approach

### 1. Preprocessing

- Remove non-content artifacts (e.g., filler words, repeated utterances, extraneous symbols).
- Normalize whitespace and fix obvious textual errors.
- Optionally, strip standard YouTube intro/outro sections to focus on core content.

### 2. Recursive and Semantic Chunking

1. **Recursive Character/Sentence Splitting**
   - Use LangChain’s `RecursiveCharacterTextSplitter` or `RecursiveTextSplitter`.
   - Split text using the following delimiter hierarchy:
     - Double newlines (`\n\n`)
     - Single newline (`\n`)
     - Sentences (`.`)
   - Ensure each chunk is within a `max_chunk_size` (default: 400 tokens) but not below a `min_chunk_size` (default: 150 tokens).

2. **Semantic Chunk Refinement**
   - Optionally apply LangChain’s `SemanticChunker` after recursion.
   - Use embedding similarity (e.g., cosine distance) to further segment dense passages at topic boundaries.
   - Adjust chunk boundaries to maximize intra-chunk semantic coherence.

3. **Chunk Overlap**
   - Implement a token overlap (default: 50 tokens, adjustable) at chunk boundaries to avoid context loss.

4. **Hierarchy Mapping**
   - Assign each chunk a unique identifier.
   - (Optional, advanced) Map child chunks (~200–400 tokens) to larger parent context blocks (~1,000–2,000 tokens) for hierarchical retrieval.

---

## Retrieval Pipeline

### 1. Indexing

- Encode each chunk (child-level) using the selected embedding model.
- Store chunk embeddings with reference to their parent context, if using hierarchy.
- Use a vector store (e.g., FAISS, Pinecone, Chroma) supporting metadata lookups.

### 2. Retrieval

- For each query:
  - Generate query embedding.
  - Retrieve top-k relevant child chunks using vector similarity (default: k=4).
  - Retrieve associated parent context blocks for candidates, if applicable.

### 3. Context Assembly

- Assemble retrieved chunks (and parents if used), deduplicating overlapping text.
- Construct context window for downstream LLM, prioritizing:
  - High semantic relevance
  - Minimal fragmentation
  - Maximal local context continuity

---

## Parameters & Tuning

| Parameter                | Default Value   | Description                                           |
|--------------------------|----------------|-----------------------------------------------------|
| max_chunk_size           | 400 tokens     | Maximum tokens per chunk                              |
| min_chunk_size           | 150 tokens     | Minimum tokens per chunk                              |
| chunk_overlap            | 50 tokens      | Tokens overlapped between consecutive chunks          |
| retrieval_top_k          | 4              | Number of top chunks retrieved for each query         |

---

## Stopword Selection Specification

### Objective

Develop a comprehensive stopword list tailored for long-form YouTube transcripts by combining established resources with an empirical analysis of domain-specific speech patterns.

### Corpus Sampling and Stopword Suggestion

1. **Transcript Sampling**
   - Randomly select 10–20 representative YouTube transcripts from the target corpus.
   - Prefer transcripts with varying speakers, topics, and typical information structures.

2. **Stopword Candidate Extraction**
   - Tokenize each sampled transcript.
   - Calculate term frequencies (absolute and relative) across the samples.
   - Identify high-frequency words common across samples, non-content words, and spoken discourse fillers such as "okay," "like," "gonna," "yeah," "uh," "um," "so," "well," "actually," "literally," "basically".
   - Cross-check these candidates against standard English stopwords.

3. **Manual Expansion and Review**
   - Merge corpus-identified words with standard stopword lists.
   - Review and curate to remove any content-relevant words accidentally flagged.

4. **Final Deliverable**
   - Save as `stopwords.txt`, one word/token per line in UTF-8 encoding.
   - Provide a short summary of custom additions and rationale.

### Starter Resources

- [NLTK English Stopwords](https://gist.github.com/sebleier/554280)  
- [Stopwords ISO (Multi-language)](https://github.com/stopwords-iso/stopwords-iso)  
- [Stopwords English](https://github.com/stopwords-iso/stopwords-en)  
- [Stop Words by Alir3z4](https://github.com/Alir3z4/stop-words)  
- [Aggregated English Stopwords](https://github.com/igorbrigadir/stopwords)  

---

## Testing and Evaluation Strategy

### Objectives

- Enable systematic experimentation with various chunking and retrieval parameter combinations.
- Measure retrieval quality and chunking efficiency to identify the best-performing configuration for the YouTube transcript corpus.

### Evaluation Dataset

- Hold out 5–10 representative transcripts with prepared benchmark queries.
- Establish expected relevant chunks/passages (ground truth) for each benchmark query with manual or expert annotation.

### Evaluation Metrics

- **Retrieval Accuracy:** Precision@k, Recall@k, and F1-score comparing retrieved chunks with ground truth.
- **Normalized Discounted Cumulative Gain (nDCG):** Measures ranking quality.
- **Chunking Efficiency:** Average chunk size, chunk count, and overlap percentages to weigh quality vs. computational cost.

### Experimental Setup

- Systematically vary parameters using grid/randomized search:  
  - max_chunk_size  
  - min_chunk_size  
  - chunk_overlap  
  - retrieval_top_k

- For each combination:
  - Chunk evaluation transcripts.
  - Build retrieval index and run benchmark queries.
  - Compute evaluation metrics.

### Reporting and Selection

- Aggregate results in tables and charts.
- Identify trade-offs between accuracy and efficiency.
- Select optimal parameters balancing performance and resource use.

### Automation Recommendations

- Integrate evaluation into CI/CD pipelines.
- Log all configurations, results, and metrics for reproducibility.
- Facilitate easy testing of new chunking/retrieval approaches.

---

## Implementation Notes

- Use LangChain chunkers and embedding retrievers where possible.
- Operate on raw transcripts with no reliance on timestamps or metadata.
- Ensure modular logging and debug outputs for chunk distribution and retrieval results.
- Regularly update stopword list with corpus-driven additions.

---

## References

- ["LangChain Chunking for RAG: Best Practices"](https://unstructured.io/blog/chunking-for-rag-best-practices)  
- ["Parent Document Retrieval in LangChain"](https://python.langchain.com/docs/how_to/parent_document_retriever/)  
- ["Effective Chunking Strategies for RAG"](https://research.trychroma.com/evaluating-chunking)  
- [NLTK Stopwords List](https://gist.github.com/sebleier/554280)  
- [Stopwords ISO Repository](https://github.com/stopwords-iso/stopwords-iso)  

---
