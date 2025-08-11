from typing import List, Dict, Any, Tuple
import os
import re
import time
from openai import OpenAI
import base64

from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from app.api.models import Citation
from app.core.retriever import build_context_for_llm

# Initialize OpenAI client
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(query: str, context: List[Dict[str, Any]]) -> Tuple[str, List[Citation]]:
    """
    Generate a response to a query using the LLM.
    
    Args:
        query: User query
        context: Retrieved context
        
    Returns:
        Tuple of (response text, list of citations)
    """
    # Build context string for LLM
    context_str = build_context_for_llm(context, query)
    
    # Check if we have any image context
    has_images = any(item.get("chunk_type") == "image" and item.get("image_path") for item in context)
    
    if has_images and LLM_MODEL.startswith("gpt-4-vision"):
        # Use vision model for multimodal context
        response = generate_multimodal_response(query, context, context_str)
    else:
        # Use text-only model
        response = generate_text_response(query, context_str)
    
    # Extract citations from response
    answer, citations = extract_citations(response, context)
    
    return answer, citations

def generate_text_response(query: str, context_str: str) -> str:
    """
    Generate a text response using the LLM.
    
    Args:
        query: User query
        context_str: Context string
        
    Returns:
        Response text
    """
    # Create system prompt
    system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
Follow these rules:
1. Answer ONLY based on the context provided
2. If the context doesn't contain relevant information, say "I don't have enough information to answer this question."
3. Include citations in your answer using [DOC_X] format, where X is the document number from the context
4. Be concise and accurate
5. If the context includes code, format it properly in your response
6. If the context includes information from images, include that in your answer when relevant"""

    # Create user prompt
    user_prompt = f"""Context:
{context_str}

Question: {query}

Please provide a helpful answer with citations."""

    # Add retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4-turbo" if LLM_MODEL.startswith("gpt-4-vision") else LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
            
            # Extract response text
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text response (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return f"I encountered an error while generating a response: {str(e)}"
            time.sleep(1)  # Wait before retrying

def generate_multimodal_response(query: str, context: List[Dict[str, Any]], context_str: str) -> str:
    """
    Generate a multimodal response using the vision model.
    
    Args:
        query: User query
        context: Retrieved context
        context_str: Context string
        
    Returns:
        Response text
    """
    # Create system prompt
    system_prompt = """You are a helpful assistant that answers questions based on the provided context, including both text and images. 
Follow these rules:
1. Answer ONLY based on the context provided (text and images)
2. If the context doesn't contain relevant information, say "I don't have enough information to answer this question."
3. Include citations in your answer using [DOC_X] format, where X is the document number from the context
4. Be concise and accurate
5. If the context includes code, format it properly in your response
6. Analyze the provided images carefully and include insights from them in your answer"""

    # Create messages with text and image content
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": f"Question: {query}\n\nPlease provide a helpful answer with citations."}
        ]}
    ]
    
    # Add text context
    messages[1]["content"].append({
        "type": "text", 
        "text": f"Text Context:\n{context_str}"
    })
    
    # Add image context
    for item in context:
        if item.get("chunk_type") == "image" and item.get("image_path"):
            image_path = item.get("image_path")
            if os.path.exists(image_path):
                try:
                    # Read image and encode as base64
                    with open(image_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    
                    # Add image to message
                    document_name = item.get("document_name", "Unknown Document")
                    page_info = f" (Page {item.get('page_number')})" if item.get("page_number") else ""
                    
                    messages[1]["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                    
                    messages[1]["content"].append({
                        "type": "text",
                        "text": f"Image from {document_name}{page_info}"
                    })
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        # Extract response text
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating multimodal response: {e}")
        return f"I encountered an error while generating a response: {str(e)}"

def extract_citations(response: str, context: List[Dict[str, Any]]) -> Tuple[str, List[Citation]]:
    """
    Extract citations from response.
    
    Args:
        response: Response text
        context: Retrieved context
        
    Returns:
        Tuple of (cleaned response, list of citations)
    """
    # Create a mapping of document IDs to document names
    doc_map = {}
    for i, item in enumerate(context):
        document_id = item.get("document_id")
        document_name = item.get("document_name", "Unknown Document")
        doc_map[document_id] = document_name
    
    # Find citations in the response
    citation_pattern = r'\[DOC_(\d+)\]'
    citation_matches = re.findall(citation_pattern, response)
    
    # Create citation objects
    citations = []
    for doc_index in citation_matches:
        try:
            doc_idx = int(doc_index) - 1
            if 0 <= doc_idx < len(context):
                item = context[doc_idx]
                document_id = item.get("document_id", "")
                document_name = item.get("document_name", "Unknown Document")
                
                # Create citation
                citation = Citation(
                    document_id=document_id,
                    document_name=document_name,
                    text=item.get("content", ""),
                    image_url=item.get("image_path") if item.get("chunk_type") == "image" else None,
                    page_number=item.get("page_number"),
                    confidence=item.get("confidence", 0.0)
                )
                
                # Add to citations if not already present
                if not any(c.document_id == citation.document_id and c.text == citation.text for c in citations):
                    citations.append(citation)
        except (ValueError, IndexError):
            continue
    
    # If no citations were found but we have context, add the top result as a citation
    if not citations and context:
        top_item = context[0]
        citations.append(Citation(
            document_id=top_item.get("document_id", ""),
            document_name=top_item.get("document_name", "Unknown Document"),
            text=top_item.get("content", ""),
            image_url=top_item.get("image_path") if top_item.get("chunk_type") == "image" else None,
            page_number=top_item.get("page_number"),
            confidence=top_item.get("confidence", 0.0)
        ))
    
    return response, citations