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
    """Evaluator for RAG system using RAGAS metrics."""

    def __init__(self):
        """Initialize evaluator with RAGAS metrics."""
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
        """Evaluate RAG performance on a dataset.

        Args:
            questions: List of questions
            answers: List of generated answers
            contexts: List of retrieved contexts (list of strings per question)
            ground_truths: List of ground truth answers

        Returns:
            Dictionary of metric scores
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
        """Evaluate a single Q&A pair.

        Args:
            question: The question
            answer: Generated answer
            contexts: Retrieved contexts
            ground_truth: Ground truth answer

        Returns:
            Dictionary of metric scores
        """
        return self.evaluate_dataset(
            questions=[question],
            answers=[answer],
            contexts=[contexts],
            ground_truths=[ground_truth]
        )