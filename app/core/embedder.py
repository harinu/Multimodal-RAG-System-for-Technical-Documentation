from typing import List, Dict, Any, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from PIL import Image
import torch
import os

from app.config import EMBEDDING_MODEL

# Initialize text embedding model
text_embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# For image embeddings, use CLIP model if available
try:
    from transformers import CLIPProcessor, CLIPModel
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    has_clip = True
except (ImportError, OSError):
    print("CLIP model not available. Using text embedding model for images.")
    has_clip = False

def embed_text(text: str) -> np.ndarray:
    """
    Generate embedding vector for text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as numpy array
    """
    if not text:
        # Return zero vector if text is empty
        return np.zeros(text_embedding_model.get_sentence_embedding_dimension())
    
    # Generate embedding
    embedding = text_embedding_model.encode(text, show_progress_bar=False)
    return embedding

def embed_image(image_path: str) -> np.ndarray:
    """
    Generate embedding vector for an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Embedding vector as numpy array
    """
    if not os.path.exists(image_path):
        # Return zero vector if image doesn't exist
        return np.zeros(512)  # CLIP uses 512-dimensional embeddings
    
    try:
        if has_clip:
            # Use CLIP model for image embedding
            image = Image.open(image_path)
            inputs = clip_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_features = clip_model.get_image_features(**inputs)
            
            # Convert to numpy and normalize
            embedding = image_features.numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        else:
            # Fall back to using OCR + text embedding if CLIP is not available
            from app.core.image_processor import extract_text_from_image
            image_text = extract_text_from_image(image_path)
            
            if image_text:
                return embed_text(image_text)
            else:
                # Return zero vector if no text was extracted
                return np.zeros(text_embedding_model.get_sentence_embedding_dimension())
    except Exception as e:
        print(f"Error embedding image: {e}")
        # Return zero vector on error
        return np.zeros(512 if has_clip else text_embedding_model.get_sentence_embedding_dimension())

def embed_code(code_info: Dict[str, Any]) -> np.ndarray:
    """
    Generate embedding vector for code snippet.
    
    Args:
        code_info: Dictionary with code information
        
    Returns:
        Embedding vector as numpy array
    """
    # Extract code snippet and language
    snippet = code_info.get("snippet", "")
    language = code_info.get("language", "unknown")
    functions = code_info.get("functions", [])
    
    if not snippet:
        # Return zero vector if snippet is empty
        return np.zeros(text_embedding_model.get_sentence_embedding_dimension())
    
    # Create a combined text representation that includes language and function information
    combined_text = f"Language: {language}\n"
    
    if functions:
        combined_text += f"Functions: {', '.join(functions)}\n\n"
    
    # Add the code snippet itself
    combined_text += snippet
    
    # Generate embedding using the text model
    return embed_text(combined_text)

def embed_chunk(chunk: Dict[str, Any]) -> np.ndarray:
    """
    Generate embedding vector for a chunk based on its type.
    
    Args:
        chunk: Dictionary with chunk information
        
    Returns:
        Embedding vector as numpy array
    """
    chunk_type = chunk.get("chunk_type", "text")
    
    if chunk_type == "text":
        return embed_text(chunk.get("content", ""))
    elif chunk_type == "image":
        return embed_image(chunk.get("image_path", ""))
    elif chunk_type == "code":
        return embed_code({
            "snippet": chunk.get("content", ""),
            "language": chunk.get("language", "unknown"),
            "functions": []
        })
    else:
        # Default to text embedding
        return embed_text(chunk.get("content", ""))