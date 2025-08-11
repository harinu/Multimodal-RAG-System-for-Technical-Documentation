from typing import List, Optional
import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.api.models import DocumentType

def validate_file_type(filename: str) -> Optional[DocumentType]:
    """
    Validate file type based on extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        DocumentType enum value or None if unsupported
    """
    file_extension = Path(filename).suffix.lower()
    
    if file_extension in [".pdf"]:
        return DocumentType.PDF
    elif file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
        return DocumentType.IMAGE
    elif file_extension in [".md"]:
        return DocumentType.MARKDOWN
    elif file_extension in [".html", ".htm"]:
        return DocumentType.HTML
    elif file_extension in [".txt"]:
        return DocumentType.TEXT
    else:
        return None

def ensure_directory(directory_path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Absolute path to the directory
    """
    abs_path = os.path.abspath(directory_path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path

def save_upload_file(upload_file: UploadFile, destination_dir: str) -> str:
    """
    Save an uploaded file to the destination directory.
    
    Args:
        upload_file: FastAPI UploadFile object
        destination_dir: Directory to save the file in
        
    Returns:
        Path to the saved file
    """
    # Ensure destination directory exists
    ensure_directory(destination_dir)
    
    # Generate file path
    file_path = os.path.join(destination_dir, upload_file.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def generate_unique_id() -> str:
    """
    Generate a unique ID.
    
    Returns:
        Unique ID string
    """
    return str(uuid.uuid4())

def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)

def get_file_extension(file_path: str) -> str:
    """
    Get file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (with dot)
    """
    return os.path.splitext(file_path)[1].lower()

def list_files_in_directory(directory_path: str, extensions: List[str] = None) -> List[str]:
    """
    List files in a directory, optionally filtered by extension.
    
    Args:
        directory_path: Path to the directory
        extensions: Optional list of extensions to filter by
        
    Returns:
        List of file paths
    """
    if not os.path.exists(directory_path):
        return []
    
    files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            if extensions is None or get_file_extension(file_path) in extensions:
                files.append(file_path)
    
    return files