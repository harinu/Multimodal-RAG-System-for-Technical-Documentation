from typing import Dict, List, Optional, Tuple, Any
import os
import shutil
from pathlib import Path

from app.api.models import DocumentType
from app.core.text_processor import extract_text_from_pdf, extract_text_from_markdown, extract_text_from_html, chunk_text
from app.core.image_processor import extract_images_from_pdf, process_image
from app.core.code_processor import extract_code_snippets, process_code
from app.core.embedder import embed_text, embed_image, embed_code
from app.db.vector_store import store_vectors, store_metadata
from app.db.metadata_store import store_document_metadata, store_chunk_metadata
from app.config import PROCESSED_DOCUMENTS_DIR

def process_document(document_id: str, file_path: str, document_type: DocumentType) -> None:
    print(f"process_document called with document_id: {document_id}, file_path: {file_path}, document_type: {document_type}")
    if not os.getenv("RAW_DOCUMENTS_DIR") or not os.getenv("PROCESSED_DOCUMENTS_DIR"):
        print("RAW_DOCUMENTS_DIR or PROCESSED_DOCUMENTS_DIR not set. Please check your environment variables.")
        return

    print(f"Processing document: {file_path} (Type: {document_type})")

    # Create directory for processed content
    processed_dir = os.path.join(PROCESSED_DOCUMENTS_DIR, document_id)
    os.makedirs(processed_dir, exist_ok=True)

    # Extract content based on document type
    print(f"Extracting content based on document type: {document_type}")
    text_chunks = []
    images = []
    code_snippets = []
    metadata = {
        "document_id": document_id,
        "filename": Path(file_path).name,
        "document_type": document_type,
    }

    if document_type == DocumentType.PDF:
        # Extract text from PDF
        text_content = extract_text_from_pdf(file_path)
        text_chunks = chunk_text(text_content)

        # Extract images from PDF
        images = extract_images_from_pdf(file_path, processed_dir)

    elif document_type == DocumentType.IMAGE:
        # Process single image
        image_info = process_image(file_path, processed_dir)
        images = [image_info] if image_info else []

    elif document_type == DocumentType.MARKDOWN:
        # Extract text from Markdown
        text_content = extract_text_from_markdown(file_path)
        text_chunks = chunk_text(text_content)

        # Extract code snippets from Markdown
        code_snippets = extract_code_snippets(text_content)

    elif document_type == DocumentType.HTML:
        # Extract text from HTML
        text_content = extract_text_from_html(file_path)
        text_chunks = chunk_text(text_content)

        # Extract code snippets from HTML
        code_snippets = extract_code_snippets(text_content)

    elif document_type == DocumentType.TEXT:
        # Process plain text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            text_chunks = chunk_text(text_content)

            # Extract potential code snippets
            code_snippets = extract_code_snippets(text_content)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            print(f"Error reading file: {e}")
            # Add basic metadata even if processing fails
            metadata["error"] = str(e)
            store_document_metadata(document_id, metadata)
            return

    print(f"Extracted {len(text_chunks)} text chunks, {len(images)} images, {len(code_snippets)} code snippets")
    print(f"Extracted content.")

    # Process and embed text chunks
    print(f"Processing and embedding content...")
    text_vectors = []
    for i, chunk in enumerate(text_chunks):
        vector = embed_text(chunk)
        chunk_id = f"{document_id}_text_{i}"
        chunk_metadata = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "chunk_type": "text",
            "content": chunk,
            "page_number": i // 2 + 1,  # Approximate page number
        }
        text_vectors.append((vector, chunk_metadata))

        # Store chunk metadata
        store_chunk_metadata(chunk_id, document_id, "text", chunk_metadata)

    # Process and embed images
    image_vectors = []
    for i, image_info in enumerate(images):
        if not image_info:
            continue

        vector = embed_image(image_info["path"])
        chunk_id = f"{document_id}_image_{i}"
        image_metadata = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "chunk_type": "image",
            "content": image_info.get("text", ""),
            "image_path": image_info["path"],
            "page_number": image_info.get("page_number", None),
            "is_diagram": image_info.get("is_diagram", False),
        }
        image_vectors.append((vector, image_metadata))

        # Store chunk metadata
        store_chunk_metadata(chunk_id, document_id, "image", image_metadata)

    # Process and embed code snippets
    code_vectors = []
    for i, snippet in enumerate(code_snippets):
        processed_snippet = process_code(snippet)
        vector = embed_code(processed_snippet)
        chunk_id = f"{document_id}_code_{i}"
        code_metadata = {
            "document_id": document_id,
            "chunk_id": chunk_id,
            "chunk_type": "code",
            "content": snippet,
            "language": processed_snippet.get("language", "unknown"),
            "functions": processed_snippet.get("functions", []),
        }
        code_vectors.append((vector, code_metadata))

        # Store chunk metadata
        store_chunk_metadata(chunk_id, document_id, "code", code_metadata)

    # Store vectors and metadata
    all_vectors = text_vectors + image_vectors + code_vectors
    if all_vectors:
        vectors, metadatas = zip(*all_vectors)
        print(f"Storing vectors and metadata...")
        store_vectors(document_id, vectors, metadatas)

    # Store document metadata
    metadata["num_text_chunks"] = len(text_chunks)
    metadata["num_images"] = len(images)
    metadata["num_code_snippets"] = len(code_snippets)
    store_metadata(document_id, metadata)
    store_document_metadata(document_id, metadata)
    print(f"Vectors and metadata stored.")

    print(f"Document processing complete: {document_id}")
    print(f"process_document complete.")
    print("process_document completed successfully.")