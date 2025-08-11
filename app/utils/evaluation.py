from typing import List, Dict, Any, Tuple
import time
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import json
import os
from pathlib import Path

from app.core.retriever import retrieve_context
from app.core.llm import generate_response

def measure_retrieval_performance(
    queries: List[str],
    relevant_doc_ids: List[List[str]],
    max_results: int = 5
) -> Dict[str, float]:
    """
    Measure retrieval performance using precision, recall, and F1 score.
    
    Args:
        queries: List of test queries
        relevant_doc_ids: List of lists of relevant document IDs for each query
        max_results: Maximum number of results to retrieve
        
    Returns:
        Dictionary with performance metrics
    """
    precisions = []
    recalls = []
    f1_scores = []
    retrieval_times = []
    
    for i, query in enumerate(queries):
        # Measure retrieval time
        start_time = time.time()
        results = retrieve_context(query=query, max_results=max_results)
        retrieval_time = time.time() - start_time
        retrieval_times.append(retrieval_time)
        
        # Get retrieved document IDs
        retrieved_doc_ids = [result["document_id"] for result in results]
        
        # Get relevant document IDs for this query
        relevant_ids = relevant_doc_ids[i] if i < len(relevant_doc_ids) else []
        
        # Calculate precision and recall
        true_positives = len(set(retrieved_doc_ids) & set(relevant_ids))
        precision = true_positives / len(retrieved_doc_ids) if retrieved_doc_ids else 0
        recall = true_positives / len(relevant_ids) if relevant_ids else 0
        
        # Calculate F1 score
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
    
    # Calculate average metrics
    avg_precision = np.mean(precisions)
    avg_recall = np.mean(recalls)
    avg_f1 = np.mean(f1_scores)
    avg_retrieval_time = np.mean(retrieval_times)
    
    return {
        "precision": avg_precision,
        "recall": avg_recall,
        "f1_score": avg_f1,
        "retrieval_time": avg_retrieval_time
    }

def evaluate_answer_quality(
    queries: List[str],
    ground_truth: List[str],
    max_results: int = 5
) -> Dict[str, float]:
    """
    Evaluate answer quality by comparing to ground truth.
    
    Args:
        queries: List of test queries
        ground_truth: List of ground truth answers
        max_results: Maximum number of results to retrieve
        
    Returns:
        Dictionary with quality metrics
    """
    response_times = []
    similarity_scores = []
    
    for i, query in enumerate(queries):
        # Retrieve context and generate response
        start_time = time.time()
        context = retrieve_context(query=query, max_results=max_results)
        answer, _ = generate_response(query, context)
        response_time = time.time() - start_time
        response_times.append(response_time)
        
        # Compare to ground truth
        if i < len(ground_truth):
            # Calculate similarity score (simple token overlap for now)
            truth_tokens = set(ground_truth[i].lower().split())
            answer_tokens = set(answer.lower().split())
            
            if truth_tokens:
                overlap = len(truth_tokens & answer_tokens)
                similarity = overlap / len(truth_tokens)
                similarity_scores.append(similarity)
    
    # Calculate average metrics
    avg_response_time = np.mean(response_times)
    avg_similarity = np.mean(similarity_scores) if similarity_scores else 0
    
    return {
        "response_time": avg_response_time,
        "answer_similarity": avg_similarity
    }

def compare_retrieval_strategies(
    queries: List[str],
    relevant_doc_ids: List[List[str]],
    strategies: List[Dict[str, Any]]
) -> Dict[str, Dict[str, float]]:
    """
    Compare different retrieval strategies.
    
    Args:
        queries: List of test queries
        relevant_doc_ids: List of lists of relevant document IDs for each query
        strategies: List of strategy configurations
        
    Returns:
        Dictionary mapping strategy names to performance metrics
    """
    results = {}
    
    for strategy in strategies:
        strategy_name = strategy.get("name", "unknown")
        max_results = strategy.get("max_results", 5)
        include_images = strategy.get("include_images", True)
        
        # Measure performance with this strategy
        performance = measure_retrieval_performance(
            queries=queries,
            relevant_doc_ids=relevant_doc_ids,
            max_results=max_results
        )
        
        results[strategy_name] = performance
    
    return results

def save_evaluation_results(results: Dict[str, Any], output_path: str):
    """
    Save evaluation results to a JSON file.
    
    Args:
        results: Evaluation results
        output_path: Path to save results to
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add timestamp
    results["timestamp"] = time.time()
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

def load_evaluation_results(input_path: str) -> Dict[str, Any]:
    """
    Load evaluation results from a JSON file.
    
    Args:
        input_path: Path to load results from
        
    Returns:
        Evaluation results
    """
    if not os.path.exists(input_path):
        return {}
    
    with open(input_path, 'r') as f:
        return json.load(f)

def create_test_set(
    queries: List[str],
    relevant_doc_ids: List[List[str]],
    ground_truth: List[str],
    output_path: str
):
    """
    Create a test set for evaluation.
    
    Args:
        queries: List of test queries
        relevant_doc_ids: List of lists of relevant document IDs for each query
        ground_truth: List of ground truth answers
        output_path: Path to save test set to
    """
    test_set = {
        "queries": queries,
        "relevant_doc_ids": relevant_doc_ids,
        "ground_truth": ground_truth
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(test_set, f, indent=2)

def load_test_set(input_path: str) -> Dict[str, Any]:
    """
    Load a test set for evaluation.
    
    Args:
        input_path: Path to load test set from
        
    Returns:
        Test set
    """
    if not os.path.exists(input_path):
        return {}
    
    with open(input_path, 'r') as f:
        return json.load(f)