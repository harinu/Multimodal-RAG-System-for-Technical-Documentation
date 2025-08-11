from typing import List, Dict, Any, Optional
import os
import json
import sqlite3
from pathlib import Path

from app.config import CHROMA_DB_DIR

# SQLite database path
DB_PATH = os.path.join(CHROMA_DB_DIR, "metadata.db")

def init_db():
    """
    Initialize the SQLite database for metadata storage.
    """
    # Create directory if it doesn't exist
    Path(CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        document_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
    ''')
    
    # Create chunks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        chunk_type TEXT NOT NULL,
        page_number INTEGER,
        metadata TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (document_id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

# Initialize database on module import
init_db()

def store_document_metadata(document_id: str, metadata: Dict[str, Any]):
    """
    Store document metadata in the database.
    
    Args:
        document_id: Document ID
        metadata: Document metadata
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract required fields
    filename = metadata.get("filename", "")
    document_type = metadata.get("document_type", "")
    
    # Convert metadata to JSON string
    metadata_json = json.dumps(metadata)
    
    # Insert or update document record
    cursor.execute(
        '''
        INSERT OR REPLACE INTO documents (document_id, filename, document_type, metadata)
        VALUES (?, ?, ?, ?)
        ''',
        (document_id, filename, document_type, metadata_json)
    )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def store_chunk_metadata(chunk_id: str, document_id: str, chunk_type: str, metadata: Dict[str, Any]):
    """
    Store chunk metadata in the database.
    
    Args:
        chunk_id: Chunk ID
        document_id: Document ID
        chunk_type: Chunk type (text, image, code)
        metadata: Chunk metadata
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract page number if available
    page_number = metadata.get("page_number")
    
    # Convert metadata to JSON string
    metadata_json = json.dumps(metadata)
    
    # Insert or update chunk record
    cursor.execute(
        '''
        INSERT OR REPLACE INTO chunks (chunk_id, document_id, chunk_type, page_number, metadata)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (chunk_id, document_id, chunk_type, page_number, metadata_json)
    )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_document_metadata(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get document metadata from the database.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document metadata or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query document record
    cursor.execute(
        "SELECT metadata FROM documents WHERE document_id = ?",
        (document_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        return None

def get_chunk_metadata(chunk_id: str) -> Optional[Dict[str, Any]]:
    """
    Get chunk metadata from the database.
    
    Args:
        chunk_id: Chunk ID
        
    Returns:
        Chunk metadata or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query chunk record
    cursor.execute(
        "SELECT metadata FROM chunks WHERE chunk_id = ?",
        (chunk_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    else:
        return None

def get_document_chunks(document_id: str, chunk_type: str = None) -> List[Dict[str, Any]]:
    """
    Get all chunks for a document.
    
    Args:
        document_id: Document ID
        chunk_type: Optional chunk type filter
        
    Returns:
        List of chunk metadata
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Prepare query
    if chunk_type:
        query = "SELECT chunk_id, metadata FROM chunks WHERE document_id = ? AND chunk_type = ?"
        params = (document_id, chunk_type)
    else:
        query = "SELECT chunk_id, metadata FROM chunks WHERE document_id = ?"
        params = (document_id,)
    
    # Execute query
    cursor.execute(query, params)
    
    # Process results
    chunks = []
    for chunk_id, metadata_json in cursor.fetchall():
        metadata = json.loads(metadata_json)
        metadata["chunk_id"] = chunk_id
        chunks.append(metadata)
    
    conn.close()
    return chunks

def get_all_documents() -> List[Dict[str, Any]]:
    """
    Get metadata for all documents.
    
    Returns:
        List of document metadata
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query all documents
    cursor.execute("SELECT document_id, filename, document_type, metadata FROM documents")
    
    # Process results
    documents = []
    for document_id, filename, document_type, metadata_json in cursor.fetchall():
        metadata = json.loads(metadata_json)
        documents.append({
            "document_id": document_id,
            "filename": filename,
            "document_type": document_type,
            **metadata
        })
    
    conn.close()
    return documents

def delete_document(document_id: str):
    """
    Delete a document and all its chunks.
    
    Args:
        document_id: Document ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete chunks first (due to foreign key constraint)
    cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    
    # Delete document
    cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()