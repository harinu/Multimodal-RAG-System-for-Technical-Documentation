import unittest
import os
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.embedder import embed_text
from app.core.retriever import retrieve_context, hybrid_search
from app.db.vector_store import store_vectors, search_vectors
from app.db.metadata_store import init_db

class TestRetriever(unittest.TestCase):
    """Test cases for the retriever module."""
    
    def setUp(self):
        """Set up test environment."""
        # Initialize test data
        self.test_texts = [
            "Python is a high-level programming language known for its readability.",
            "FastAPI is a modern web framework for building APIs with Python.",
            "Vector databases store and retrieve high-dimensional vectors efficiently.",
            "Retrieval-augmented generation combines search with language models.",
            "Image processing involves manipulating digital images using algorithms."
        ]
        
        # Create test document ID
        self.test_doc_id = "test_document_001"
        
        # Create test embeddings
        self.test_vectors = []
        self.test_metadatas = []
        
        for i, text in enumerate(self.test_texts):
            # Generate embedding
            vector = embed_text(text)
            
            # Create metadata
            metadata = {
                "document_id": self.test_doc_id,
                "chunk_id": f"{self.test_doc_id}_text_{i}",
                "chunk_type": "text",
                "content": text,
                "page_number": i + 1
            }
            
            self.test_vectors.append(vector)
            self.test_metadatas.append(metadata)
    
    def test_search_vectors(self):
        """Test vector search functionality."""
        # Store test vectors
        store_vectors(self.test_doc_id, self.test_vectors, self.test_metadatas)
        
        # Create query vector
        query = "What is Python programming?"
        query_vector = embed_text(query)
        
        # Search vectors
        results = search_vectors(query_vector, max_results=2)
        
        # Verify results
        self.assertEqual(len(results), 2, "Should return 2 results")
        self.assertEqual(results[0]["metadata"]["document_id"], self.test_doc_id, 
                         "Should return results from the test document")
        
        # The first result should be about Python
        self.assertIn("Python", results[0]["metadata"]["content"], 
                      "First result should be about Python")
    
    def test_hybrid_search(self):
        """Test hybrid search functionality."""
        # Create mock vector results
        vector_results = [
            {
                "chunk_id": "doc1_text_1",
                "document_id": "doc1",
                "content": "Python is a programming language with clear syntax.",
                "confidence": 0.8
            },
            {
                "chunk_id": "doc1_text_2",
                "document_id": "doc1",
                "content": "JavaScript is used for web development.",
                "confidence": 0.7
            }
        ]
        
        # Test query with keyword match
        query = "Python programming"
        results = hybrid_search(query, vector_results)
        
        # Verify that Python result got boosted
        self.assertEqual(results[0]["chunk_id"], "doc1_text_1", 
                         "Python result should be ranked first")
        self.assertGreater(results[0]["confidence"], 0.8, 
                           "Confidence should be boosted for keyword match")
    
    def test_retrieve_context(self):
        """Test context retrieval functionality."""
        # Store test vectors first
        store_vectors(self.test_doc_id, self.test_vectors, self.test_metadatas)
        
        # Retrieve context
        query = "Tell me about vector databases"
        context = retrieve_context(query, max_results=3)
        
        # Verify context
        self.assertGreaterEqual(len(context), 1, "Should return at least one context item")
        
        # Check if the most relevant result is about vector databases
        found_vector_db = False
        for item in context:
            if "vector database" in item.get("content", "").lower():
                found_vector_db = True
                break
        
        self.assertTrue(found_vector_db, "Should return context about vector databases")


if __name__ == '__main__':
    # Initialize database before running tests
    init_db()
    
    # Run tests
    unittest.main()