from typing import List, Dict, Any
import re
from pypdf import PdfReader
import markdown
from bs4 import BeautifulSoup

from app.config import TEXT_CHUNK_SIZE, TEXT_CHUNK_OVERLAP

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return text

def extract_text_from_markdown(markdown_path: str) -> str:
    """
    Extract text content from a Markdown file.
    
    Args:
        markdown_path: Path to the Markdown file
        
    Returns:
        Extracted text content
    """
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)
        
        # Extract text from HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\n\n')
        
        return text
    except Exception as e:
        print(f"Error extracting text from Markdown: {e}")
        return ""

def extract_text_from_html(html_path: str) -> str:
    """
    Extract text content from an HTML file.
    
    Args:
        html_path: Path to the HTML file
        
    Returns:
        Extracted text content
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract text from HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator='\n\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return ""

def chunk_text(text: str) -> List[str]:
    """
    Split text into chunks of specified size with overlap.
    
    Args:
        text: Text to chunk
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size, save current chunk and start a new one
        if len(current_chunk) + len(paragraph) > TEXT_CHUNK_SIZE and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            words = current_chunk.split()
            overlap_words = words[-min(len(words), TEXT_CHUNK_OVERLAP // 10):]
            current_chunk = ' '.join(overlap_words) + '\n\n' + paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += '\n\n' + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks