"""
Evaluation module for RAG system performance.

Implements metrics from RAGAS framework: context precision, context recall,
faithfulness, and answer relevancy.
"""

from typing import List, Dict, Any
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)
from datasets import Dataset


class RAGEvaluator:
    """Evaluator for RAG system performance using RAGAS framework.

    Provides comprehensive evaluation of retrieval-augmented generation systems
    using industry-standard metrics. Specifically designed for assessing
    business content Q&A systems with focus on factual accuracy and relevance.
    """

    def __init__(self):
        """Initialize evaluator with standard RAGAS metrics.

        Sets up the four core evaluation metrics:
        - Context Precision: Relevance of retrieved documents
        - Context Recall: Completeness of retrieved information
        - Faithfulness: Groundedness of answers in retrieved context
        - Answer Relevancy: Alignment of answers with questions
        """
        self.metrics = [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy
        ]

    def evaluate_dataset(self,
                        questions: List[str],
                        answers: List[str],
                        contexts: List[List[str]],
                        ground_truths: List[str]) -> Dict[str, float]:
        """Evaluate RAG performance on a complete dataset.

        Runs comprehensive evaluation across multiple Q&A pairs to assess
        overall system performance on business content queries.

        Args:
            questions: List of business-related questions from users
            answers: List of generated answers from the RAG system
            contexts: List of retrieved context chunks for each question,
                     where each context is a list of strings
            ground_truths: List of verified correct answers for comparison

        Returns:
            Dictionary containing average scores for each metric:
            - context_precision: Average precision of retrieved contexts
            - context_recall: Average recall of relevant information
            - faithfulness: Average faithfulness to retrieved context
            - answer_relevancy: Average relevance of answers to questions
        """
        # Prepare dataset
        data = {
            'question': questions,
            'answer': answers,
            'contexts': contexts,
            'ground_truth': ground_truths
        }

        dataset = Dataset.from_dict(data)

        # Run evaluation
        results = evaluate(dataset, metrics=self.metrics)

        return results

    def evaluate_single(self,
                       question: str,
                       answer: str,
                       contexts: List[str],
                       ground_truth: str) -> Dict[str, float]:
        """Evaluate a single Q&A interaction.

        Useful for real-time evaluation of individual queries or for
        debugging specific cases in the business content domain.

        Args:
            question: A single business-related question
            answer: The generated answer from the RAG system
            contexts: List of retrieved context strings for this question
            ground_truth: The verified correct answer for comparison

        Returns:
            Dictionary with individual metric scores for this Q&A pair
        """
        return self.evaluate_dataset(
            questions=[question],
            answers=[answer],
            contexts=[contexts],
            ground_truths=[ground_truth]
        )