from typing import List, Dict, Any, Optional
import numpy as np
import re
from collections import defaultdict

from app.core.embedder import embed_text
from app.db.vector_store import search_vectors
from app.db.metadata_store import get_chunk_metadata, get_document_metadata

def retrieve_context(
    query: str,
    document_ids: Optional[List[str]] = None,
    include_images: bool = True,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context for a query.
    
    Args:
        query: User query
        document_ids: Optional list of document IDs to search in
        include_images: Whether to include image results
        max_results: Maximum number of results to return
        
    Returns:
        List of context items with metadata
    """
    # Generate query embedding
    query_vector = embed_text(query)
    
    # Perform vector search
    search_results = search_vectors(
        query_vector=query_vector,
        document_ids=document_ids,
        include_images=include_images,
        max_results=max_results
    )
    
    # Enhance results with additional metadata
    enhanced_results = []
    for result in search_results:
        chunk_id = result["id"]
        metadata = result["metadata"]
        document_id = metadata.get("document_id")
        
        # Get document metadata
        document_metadata = get_document_metadata(document_id)
        if document_metadata:
            document_name = document_metadata.get("filename", "Unknown Document")
        else:
            document_name = "Unknown Document"
        
        # Create enhanced result
        enhanced_result = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "document_name": document_name,
            "chunk_type": metadata.get("chunk_type", "text"),
            "content": metadata.get("content", ""),
            "page_number": metadata.get("page_number"),
            "confidence": result["confidence"],
        }
        
        # Add image path if it's an image
        if enhanced_result["chunk_type"] == "image":
            enhanced_result["image_path"] = metadata.get("image_path")
        
        # Add language if it's code
        if enhanced_result["chunk_type"] == "code":
            enhanced_result["language"] = metadata.get("language", "unknown")
        
        enhanced_results.append(enhanced_result)
    
    # Perform hybrid search to improve results
    if query and enhanced_results:
        enhanced_results = hybrid_search(query, enhanced_results)
    
    return enhanced_results

def hybrid_search(query: str, vector_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance vector search results with keyword matching.
    
    Args:
        query: User query
        vector_results: Results from vector search
        
    Returns:
        Reranked results
    """
    # Extract keywords from query (words with 4+ chars)
    keywords = re.findall(r'\b\w{4,}\b', query.lower())
    
    if not keywords:
        return vector_results  # No keywords to match
    
    # Score results based on keyword matches
    for result in vector_results:
        content = result.get("content", "").lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword in content)
        
        # Adjust confidence based on keyword matches
        if keyword_matches > 0:
            # Boost confidence based on keyword matches (max boost of 0.2)
            keyword_boost = min(0.2, 0.05 * keyword_matches)
            result["confidence"] = min(0.99, result["confidence"] + keyword_boost)
    
    # Re-sort results by confidence
    vector_results.sort(key=lambda x: x["confidence"], reverse=True)
    
    return vector_results

def group_results_by_document(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group results by document.
    
    Args:
        results: List of search results
        
    Returns:
        Dictionary mapping document IDs to lists of results
    """
    grouped = defaultdict(list)
    
    for result in results:
        document_id = result.get("document_id")
        if document_id:
            grouped[document_id].append(result)
    
    return dict(grouped)

def build_context_for_llm(results: List[Dict[str, Any]], query: str) -> str:
    """
    Build context string for LLM from search results.
    
    Args:
        results: List of search results
        query: User query
        
    Returns:
        Context string for LLM
    """
    if not results:
        return "No relevant information found."
    
    # Group results by document
    grouped = group_results_by_document(results)
    
    context_parts = []
    
    # Add query
    context_parts.append(f"Query: {query}\n\n")
    
    # Add context from each document
    for document_id, doc_results in grouped.items():
        # Get document name from first result
        document_name = doc_results[0].get("document_name", "Unknown Document")
        
        context_parts.append(f"Document: {document_name}\n")
        
        # Sort results by page number if available
        doc_results.sort(key=lambda x: (x.get("page_number") or 9999, x.get("chunk_id", "")))
        
        # Add each result
        for result in doc_results:
            chunk_type = result.get("chunk_type", "text")
            
            if chunk_type == "text":
                content = result.get("content", "")
                page = result.get("page_number")
                page_info = f" (Page {page})" if page else ""
                
                context_parts.append(f"Text{page_info}:\n{content}\n")
                
            elif chunk_type == "image":
                image_text = result.get("content", "")
                image_path = result.get("image_path", "")
                page = result.get("page_number")
                page_info = f" (Page {page})" if page else ""
                
                if image_text:
                    context_parts.append(f"Image{page_info} text:\n{image_text}\n")
                else:
                    context_parts.append(f"Image{page_info}: [Image at {image_path}]\n")
                
            elif chunk_type == "code":
                content = result.get("content", "")
                language = result.get("language", "unknown")
                
                context_parts.append(f"Code ({language}):\n{content}\n")
        
        context_parts.append("\n")
    
    return "\n".join(context_parts)