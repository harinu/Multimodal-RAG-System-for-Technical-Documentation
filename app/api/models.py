from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DocumentType(str, Enum):
    """Enum for document types"""
    PDF = "pdf"
    IMAGE = "image"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class UploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    document_type: DocumentType
    status: str
    message: str


class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""
    query: str
    document_ids: Optional[List[str]] = None
    include_images: bool = True
    max_results: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    """Model for citation information"""
    document_id: str
    document_name: str
    text: Optional[str] = None
    image_url: Optional[str] = None
    page_number: Optional[int] = None
    confidence: float


class QueryResponse(BaseModel):
    """Response model for query results"""
    query: str
    answer: str
    citations: List[Citation]
    processing_time: float