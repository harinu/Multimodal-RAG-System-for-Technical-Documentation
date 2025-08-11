from typing import List, Dict, Any, Tuple, Optional
import os
import json
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

from app.config import CHROMA_DB_DIR

# Initialize ChromaDB client
try:
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    # Fallback to in-memory client
    client = chromadb.Client()

# Create embedding function that accepts pre-computed embeddings
embedding_function = embedding_functions.DefaultEmbeddingFunction()

def get_collection(document_id: str = None):
    """
    Get or create a ChromaDB collection.
    
    Args:
        document_id: Optional document ID to create a collection specific to a document
        
    Returns:
        ChromaDB collection
    """
    if document_id:
        # Create a collection for a specific document
        collection_name = f"document_{document_id}"
    else:
        # Use a default collection for all documents
        collection_name = "all_documents"
    
    # Get or create collection
    try:
        collection = client.get_collection(name=collection_name)
    except ValueError:
        # Collection doesn't exist, create it
        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    
    return collection

def store_vectors(document_id: str, vectors: List[np.ndarray], metadatas: List[Dict[str, Any]]):
    """
    Store vectors and metadata in ChromaDB.
    
    Args:
        document_id: Document ID
        vectors: List of embedding vectors
        metadatas: List of metadata dictionaries
    """
    if not vectors or not metadatas:
        return
    
    # Get collection for this document
    collection = get_collection(document_id)
    
    # Prepare IDs, embeddings, and metadata
    ids = [metadata["chunk_id"] for metadata in metadatas]
    
    # Convert numpy arrays to lists for ChromaDB
    embeddings = [vector.tolist() for vector in vectors]
    
    # Extract document content for ChromaDB
    documents = [metadata.get("content", "") for metadata in metadatas]
    
    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    # Also add to the combined collection
    combined_collection = get_collection()
    combined_collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

def store_metadata(document_id: str, metadata: Dict[str, Any]):
    """
    Store document metadata.
    
    Args:
        document_id: Document ID
        metadata: Document metadata
    """
    # Create metadata directory if it doesn't exist
    metadata_dir = os.path.join(CHROMA_DB_DIR, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Save metadata to file
    metadata_path = os.path.join(metadata_dir, f"{document_id}.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

def get_document_metadata(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get document metadata.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document metadata or None if not found
    """
    metadata_path = os.path.join(CHROMA_DB_DIR, "metadata", f"{document_id}.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    with open(metadata_path, 'r') as f:
        return json.load(f)

def get_document_ids() -> List[str]:
    """
    Get all document IDs.
    
    Returns:
        List of document IDs
    """
    metadata_dir = os.path.join(CHROMA_DB_DIR, "metadata")
    
    if not os.path.exists(metadata_dir):
        return []
    
    # Get all JSON files in metadata directory
    document_ids = []
    for filename in os.listdir(metadata_dir):
        if filename.endswith(".json"):
            document_ids.append(filename[:-5])  # Remove .json extension
    
    return document_ids

def search_vectors(
    query_vector: np.ndarray,
    document_ids: List[str] = None,
    include_images: bool = True,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors.
    
    Args:
        query_vector: Query embedding vector
        document_ids: Optional list of document IDs to search in
        include_images: Whether to include image results
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with metadata
    """
    # Use the combined collection
    collection = get_collection()
    
    # Prepare query filter
    query_filter = None
    if document_ids:
        query_filter = {"document_id": {"$in": document_ids}}
    
    if not include_images:
        if query_filter:
            query_filter = {
                "$and": [
                    query_filter,
                    {"chunk_type": {"$ne": "image"}}
                ]
            }
        else:
            query_filter = {"chunk_type": {"$ne": "image"}}
    
    # Query the collection
    results = collection.query(
        query_embeddings=[query_vector.tolist()],
        n_results=max_results,
        where=query_filter
    )
    
    # Process results
    processed_results = []
    if results["ids"] and results["ids"][0]:
        for i, result_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i] if "distances" in results else 0.0
            
            # Convert distance to confidence score (1.0 - normalized_distance)
            confidence = 1.0 - min(distance / 2.0, 0.95)  # Normalize and cap at 0.95
            
            processed_results.append({
                "id": result_id,
                "metadata": metadata,
                "confidence": confidence
            })
    
    return processed_results