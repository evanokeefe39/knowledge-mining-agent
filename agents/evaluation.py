"""
Evaluation module for RAG system performance using DeepEval.

Implements comprehensive RAG evaluation metrics:
- Answer Relevancy: How relevant is the answer to the question
- Faithfulness: How factually consistent is the answer with the context
- Contextual Relevancy: How relevant is the retrieved context to the question
- Contextual Recall: How much of the ground truth information is recalled
- Contextual Precision: How precise is the retrieved context
"""

from typing import List, Dict, Any, Union
import numpy as np
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric
)
from deepeval.test_case import LLMTestCase


class RAGEvaluator:
    """Evaluator for RAG system performance using DeepEval metrics.

    Uses DeepEval's comprehensive suite of RAG evaluation metrics for
    thorough assessment of retrieval-augmented generation systems.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize evaluator with DeepEval metrics.

        Args:
            model: LLM model to use for evaluation judgments
        """
        self.model = model
        self.metrics = [
            AnswerRelevancyMetric(model=model, threshold=0.7),
            FaithfulnessMetric(model=model, threshold=0.7),
            ContextualRelevancyMetric(model=model, threshold=0.7),
            ContextualRecallMetric(model=model, threshold=0.7),
            ContextualPrecisionMetric(model=model, threshold=0.7)
        ]

    def evaluate_dataset(self,
                         questions: List[str],
                         answers: List[str],
                         contexts: List[List[str]],
                         ground_truths: List[str]) -> Dict[str, Any]:
        """Evaluate RAG performance on a complete dataset using DeepEval.

        Args:
            questions: List of questions
            answers: List of generated answers
            contexts: List of retrieved context chunks (list of lists)
            ground_truths: List of verified correct answers

        Returns:
            Dictionary with evaluation results from all metrics
        """
        # Create test cases for DeepEval
        test_cases = []
        for question, answer, context_list, ground_truth in zip(
            questions, answers, contexts, ground_truths
        ):
            # Join context chunks into a single string
            context = "\n\n".join(context_list) if context_list else ""

            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                expected_output=ground_truth,
                retrieval_context=context_list  # DeepEval expects list of strings
            )
            test_cases.append(test_case)

        # Run evaluation
        evaluation_results = evaluate(
            test_cases=test_cases,
            metrics=self.metrics,
            print_results=False  # We'll format our own output
        )

        # Aggregate results
        results = {}
        for metric in self.metrics:
            metric_name = metric.__class__.__name__.replace('Metric', '').lower()
            scores = [result.score for result in evaluation_results if result.metric == metric.__class__.__name__]
            if scores:
                results[f"{metric_name}_mean"] = np.mean(scores)
                results[f"{metric_name}_std"] = np.std(scores)
                results[f"{metric_name}_min"] = np.min(scores)
                results[f"{metric_name}_max"] = np.max(scores)

        return results

    def evaluate_retrieval(self,
                            retrieved_chunk_ids: List[List[str]],
                            ground_truth_chunk_ids: List[List[str]],
                            k: int = 4) -> Dict[str, float]:
        """Legacy method for backward compatibility - now uses DeepEval metrics.

        This method is kept for compatibility but evaluation should use evaluate_dataset
        for comprehensive assessment.

        Args:
            retrieved_chunk_ids: List of lists of retrieved chunk IDs for each query
            ground_truth_chunk_ids: List of lists of ground truth relevant chunk IDs
            k: Number of top results to evaluate

        Returns:
            Dict with basic retrieval statistics
        """
        precisions = []
        recalls = []

        for retrieved, ground_truth in zip(retrieved_chunk_ids, ground_truth_chunk_ids):
            # Convert to sets for intersection
            retrieved_set = set(retrieved[:k])
            ground_truth_set = set(ground_truth)

            # Precision@k: fraction of retrieved that are relevant
            if retrieved_set:
                precision = len(retrieved_set & ground_truth_set) / len(retrieved_set)
            else:
                precision = 0.0
            precisions.append(precision)

            # Recall@k: fraction of relevant that are retrieved
            if ground_truth_set:
                recall = len(retrieved_set & ground_truth_set) / len(ground_truth_set)
            else:
                recall = 0.0
            recalls.append(recall)

        return {
            f'precision@{k}': np.mean(precisions),
            f'recall@{k}': np.mean(recalls)
        }