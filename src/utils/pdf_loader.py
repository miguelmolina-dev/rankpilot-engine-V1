import fitz  # PyMuPDF
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file located at file_path.
    Optimized for memory efficiency on Ubuntu servers.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    text_content = []
    
    try:
        # Open the document
        with fitz.open(file_path) as doc:
            for page in doc:
                # We use .get_text() with "text" flags to get clean strings
                text_content.append(page.get_text("text"))
        
        # Join with double newlines to maintain some structural separation
        return "\n\n".join(text_content)
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def clean_extracted_text(text: str) -> str:
    """
    Optional: Basic cleaning to remove excessive whitespace or 
    non-printable characters before sending to the LLM.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)