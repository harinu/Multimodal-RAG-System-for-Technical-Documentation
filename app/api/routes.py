from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
import time
import shutil
from pathlib import Path

from app.api.models import UploadResponse, QueryRequest, QueryResponse, DocumentType, Citation
from app.config import RAW_DOCUMENTS_DIR

# Import core functionality
from app.core.document_processor import process_document
from app.core.retriever import retrieve_context
from app.core.llm import generate_response
from app.db.vector_store import get_document_ids

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a document for processing and indexing.
    
    The document will be saved and processed in the background.
    """
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Determine document type from file extension
    file_extension = Path(file.filename).suffix.lower()
    document_type = None
    
    if file_extension in [".pdf"]:
        document_type = DocumentType.PDF
    elif file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        document_type = DocumentType.IMAGE
    elif file_extension in [".md"]:
        document_type = DocumentType.MARKDOWN
    elif file_extension in [".html", ".htm"]:
        document_type = DocumentType.HTML
    elif file_extension in [".txt"]:
        document_type = DocumentType.TEXT
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    # Create directory for document
    document_dir = os.path.join(RAW_DOCUMENTS_DIR, document_id)
    print(f"Creating directory: {document_dir}")
    os.makedirs(document_dir, exist_ok=True)
    print(f"Directory created: {document_dir}")
    
    # Save file
    file_path = os.path.join(document_dir, file.filename)
    print(f"Saving file to: {file_path}")
    print(f"File size: {file.size}, File type: {file.content_type}")
    print(f"Saving file...")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"File saved successfully to: {file_path}")
    print(f"File saved.")
    # Process document in background
    print(f"Calling process_document for document_id: {document_id}, file_path: {file_path}, document_type: {document_type}")
    background_tasks.add_task(process_document, document_id, file_path, document_type)
    print(f"process_document called.")
    
    response = UploadResponse(
        document_id=document_id,
        filename=file.filename,
        document_type=document_type,
        status="processing",
        message="Document uploaded and processing started"
    )
    print(f"Response: {response}")
    return response

@router.get("/documents")
async def list_documents():
    """
    List all available documents.
    """
    # Get document IDs from vector store
    document_ids = get_document_ids()
    
    return {"document_ids": document_ids}

@router.get("/documents/{document_id}/metadata")
async def get_document_metadata_endpoint(document_id: str):
    """
    Get metadata for a specific document.
    """
    metadata = get_document_metadata(document_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    return metadata

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Returns an answer with relevant citations.
    """
    start_time = time.time()
    
    # Retrieve relevant context
    context = retrieve_context(
        query=request.query,
        document_ids=request.document_ids,
        include_images=request.include_images,
        max_results=request.max_results
    )
    
    # Handle case where no context is found
    if not context:
        return QueryResponse(
            query=request.query,
            answer="No relevant information found for your query.",
            citations=[],
            processing_time=time.time() - start_time
        )
    
    # Generate response using LLM
    answer, citations = generate_response(request.query, context)
    
    processing_time = time.time() - start_time
    
    return QueryResponse(
        query=request.query,
        answer=answer,
        citations=citations,
        processing_time=processing_time
    )

@router.get("/documents/{document_id}/raw/{filename}")
async def get_raw_document(document_id: str, filename: str):
    """
    Retrieve a raw document file.
    """
    file_path = os.path.join(RAW_DOCUMENTS_DIR, document_id, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
    
    return FileResponse(file_path)