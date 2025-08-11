from typing import List, Dict, Any, Optional
import os
import uuid
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

def extract_images_from_pdf(pdf_path: str, output_dir: str) -> List[Dict[str, Any]]:
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        
    Returns:
        List of dictionaries with image information
    """
    images_info = []
    
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        
        # Iterate through pages
        for page_num, page in enumerate(pdf_document):
            # Get images from page
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                # Get image data
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Generate image file name
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{base_image['ext']}"
                image_path = os.path.join(output_dir, image_filename)
                
                # Save image
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                # Process image for OCR
                image_text = extract_text_from_image(image_path)
                
                # Add image info
                images_info.append({
                    "path": image_path,
                    "page_number": page_num + 1,
                    "text": image_text,
                    "width": base_image["width"],
                    "height": base_image["height"]
                })
        
        pdf_document.close()
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")
    
    return images_info

def process_image(image_path: str, output_dir: str) -> Optional[Dict[str, Any]]:
    """
    Process a single image file.
    
    Args:
        image_path: Path to the image file
        output_dir: Directory to save processed image
        
    Returns:
        Dictionary with image information or None if processing fails
    """
    try:
        # Copy image to output directory
        image_filename = Path(image_path).name
        output_path = os.path.join(output_dir, image_filename)
        
        if image_path != output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            Image.open(image_path).save(output_path)
        
        # Extract text from image using OCR
        image_text = extract_text_from_image(output_path)
        
        # Get image dimensions
        img = Image.open(output_path)
        width, height = img.size
        
        # Check if image contains diagrams
        is_diagram = detect_diagrams(output_path)
        
        return {
            "path": output_path,
            "text": image_text,
            "width": width,
            "height": height,
            "is_diagram": is_diagram
        }
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text
    """
    try:
        # Use pytesseract for OCR
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def detect_diagrams(image_path: str) -> bool:
    """
    Detect if an image contains diagrams or flowcharts.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if the image likely contains diagrams, False otherwise
    """
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return False
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        # Count horizontal and vertical lines
        horizontal_lines = 0
        vertical_lines = 0
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > abs(y2 - y1):
                    horizontal_lines += 1
                else:
                    vertical_lines += 1
        
        # If there are many horizontal and vertical lines, it's likely a diagram
        return horizontal_lines > 5 and vertical_lines > 5
    except Exception as e:
        print(f"Error detecting diagrams: {e}")
        return False