#!/usr/bin/env python3
"""
Run evaluations against the baseline RAG agent using real Hormozi transcript data.

This script uses the actual RAG agent from the app and evaluates its performance
against real Alex Hormozi content using the DeepEval evaluation framework.
"""

import sys
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Dict, Any
from agents.baseline_rag_agent import BaselineRAGAgent
from agents.evaluation import RAGEvaluator
from agents.data_preprocessing import BusinessContentPreprocessor
from config import config


def load_evaluation_dataset_from_json(json_path: str = "eval_dataset.json") -> Dict[str, Any]:
    """Load evaluation dataset from JSON file with explicit chunks and metadata."""
    print(f"Loading evaluation dataset from {json_path}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = []
    ground_truths = []
    relevant_chunks = []  # List of chunk objects with text and metadata

    for item in data['questions']:
        questions.append(item['question'])
        ground_truths.append(item['ground_truth'])
        relevant_chunks.append(item['relevant_chunks'])  # List of chunk dicts

    print(f"Loaded {len(questions)} evaluation questions from JSON")

    return {
        'questions': questions,
        'ground_truths': ground_truths,
        'relevant_chunks': relevant_chunks,  # Explicit chunks instead of IDs
        'metadata': data.get('metadata', {})
    }


def run_evaluation_with_grid_search():
    """Run evaluation with grid search over chunking parameters."""
    print("[START] Starting evaluation with grid search over chunking parameters...")

    # Get evaluation dataset from JSON
    eval_data = load_evaluation_dataset_from_json()
    questions = eval_data['questions']
    ground_truths = eval_data['ground_truths']
    relevant_chunks = eval_data['relevant_chunks']  # List of lists of chunk dicts

    # Extract unique video IDs from the evaluation dataset
    video_ids = set()
    for chunk_list in relevant_chunks:
        for chunk in chunk_list:
            video_ids.add(chunk['metadata']['video_id'])

    print(f"Evaluation dataset covers {len(video_ids)} unique videos")

    # Fetch the corresponding transcripts
    connection_string = (
        f"postgresql://{config.get('SUPABASE__DB_USER')}:"
        f"{config.get('SUPABASE__DB_PASSWORD')}@"
        f"{config.get('SUPABASE__DB_HOST')}:"
        f"{config.get('SUPABASE__DB_PORT')}/"
        f"{config.get('SUPABASE__DB_NAME')}"
    )

    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch transcripts for videos in eval dataset
    video_ids_list = list(video_ids)
    placeholders = ','.join(['%s'] * len(video_ids_list))
    cursor.execute(f"""
        SELECT video_id, video_name, transcript, transcript_summary
        FROM {config.get('database', {}).get('schema', 'dw')}.fact_youtube_transcripts
        WHERE video_id IN ({placeholders})
    """, video_ids_list)

    eval_transcripts = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"Fetched {len(eval_transcripts)} transcripts for evaluation")

    # Define parameter grid
    param_grid = [
        {'max_chunk_size': 300, 'min_chunk_size': 100, 'chunk_overlap': 30},
        {'max_chunk_size': 400, 'min_chunk_size': 150, 'chunk_overlap': 50},
        {'max_chunk_size': 500, 'min_chunk_size': 200, 'chunk_overlap': 75},
    ]

    results_summary = []

    for params in param_grid:
        print(f"\n[PARAMS] Testing parameters: {params}")

        # Preprocess transcripts with current parameters
        preprocessor = BusinessContentPreprocessor(
            max_chunk_size=params['max_chunk_size'],
            min_chunk_size=params['min_chunk_size'],
            chunk_overlap=params['chunk_overlap'],
            use_semantic_refinement=False,  # Disable for faster evaluation
            use_hierarchy=False  # Disable for faster evaluation
        )

        # Process evaluation transcripts
        transcripts = []
        for row in eval_transcripts:
            content = row['transcript'] or row['transcript_summary']
            if content:
                metadata = {
                    'video_id': row['video_id'],
                    'title': row['video_name'],
                    'source': 'youtube_transcript'
                }
                transcripts.append({'text': content, 'metadata': metadata})

        documents = preprocessor.preprocess_batch(transcripts)
        print(f"[OK] Created {len(documents)} chunks")

        # Initialize RAG agent with processed documents
        rag_agent = BaselineRAGAgent()
        rag_agent.load_documents(documents)
        rag_agent.initialize_agent()

        # Get answers
        answers = []
        contexts = []
        retrieved_chunk_ids = []

        for i, question in enumerate(questions):
            try:
                # Get context using agent's retrieval
                context = rag_agent._retrieve_context(question, top_k=4)
                # For now, create mock chunk IDs (we'll improve this)
                chunk_ids = [f"chunk_{j}" for j in range(len(context.split('\n\n')))]
                retrieved_chunk_ids.append(chunk_ids)

                # Generate answer
                answer = rag_agent.query(question)
                answers.append(answer)
                contexts.append([context])  # Wrap in list for evaluator

            except Exception as e:
                print(f"[WARN] Failed to answer question {i}: {e}")
                answers.append("Error generating answer")
                contexts.append([])
                retrieved_chunk_ids.append([])

        # Create ground truth chunk IDs from relevant_chunks
        ground_truth_chunk_ids = []
        for chunk_list in relevant_chunks:
            # Use chunk text hash as ID for now
            chunk_ids = [f"gt_chunk_{hash(chunk['text'][:100])}" for chunk in chunk_list]
            ground_truth_chunk_ids.append(chunk_ids)

        # Evaluate using DeepEval
        evaluator = RAGEvaluator()
        results = evaluator.evaluate_dataset(
            questions=questions,
            answers=answers,
            contexts=contexts,
            ground_truths=ground_truths
        )

        # Add basic chunking statistics (DeepEval doesn't provide chunking efficiency metrics)
        results.update({
            'num_chunks': len(documents),
            'avg_chunk_size': np.mean([len(doc.page_content.split()) for doc in documents]) if documents else 0,
            'chunk_params': params
        })

        results_summary.append({
            'params': params,
            'metrics': results,
            'num_chunks': len(documents)
        })

        print(f"[RESULTS] {params}: {results}")

    # Write markdown report
    with open('eval_report.md', 'w', encoding='utf-8') as f:
        f.write("# RAG Evaluation Report\n\n")
        f.write("## Grid Search Results Summary\n\n")

        for result in results_summary:
            params = result['params']
            metrics = result['metrics']
            f.write(f"### Parameters: {params}\n")
            f.write(f"- Number of chunks: {result['num_chunks']}\n")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    f.write(f"- {metric}: {value:.3f}\n")
                else:
                    f.write(f"- {metric}: {value}\n")
            f.write("\n")

        # Find best configuration
        if results_summary:
            # Simple heuristic: balance answer relevancy and faithfulness
            best_result = max(results_summary,
                              key=lambda x: (x['metrics'].get('answer_relevancy_mean', 0) +
                                           x['metrics'].get('faithfulness_mean', 0)) / 2)
            f.write("## Best Configuration\n\n")
            f.write(f"**Recommended parameters:** {best_result['params']}\n\n")
            f.write("**Metrics:**\n")
            for metric, value in best_result['metrics'].items():
                if isinstance(value, float):
                    f.write(f"- {metric}: {value:.3f}\n")
                else:
                    f.write(f"- {metric}: {value}\n")

    print("Evaluation report written to eval_report.md")


if __name__ == "__main__":
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    run_evaluation_with_grid_search()