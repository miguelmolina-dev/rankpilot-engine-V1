import fitz  # PyMuPDF
import docx
import base64
import io

def extract_text_from_base64(base64_string: str) -> str:
    """
    Extracts all text from a base64 encoded document (PDF or DOCX).
    """

    print("--- [Document Loader] Extracting text from base64 input ---")
    if "base64," in base64_string:
        base64_string = base64_string.split("base64,")[1]

    try:
        file_bytes = base64.b64decode(base64_string)
        print(f"--- [Document Loader] Successfully decoded base64 string, byte size: {len(file_bytes)} ---")
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return ""

    if file_bytes.startswith(b"%PDF"):
        text_content = []
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text_content.append(page.get_text("text"))
                print(f"--- [Document Loader] Extracted text from PDF, total characters: {sum(len(t) for t in text_content)} ---")
            return "\n\n".join(text_content)
        except Exception as e:
            print(f"Error parsing base64 PDF: {e}")
            return ""
    elif file_bytes.startswith(b"PK\x03\x04"):
        try:
            doc_obj = docx.Document(io.BytesIO(file_bytes))
            text_content = [para.text for para in doc_obj.paragraphs]
            print(f"--- [Document Loader] Extracted text from DOCX, total characters: {sum(len(t) for t in text_content)} ---")
            return "\n\n".join(text_content)
        except Exception as e:
            print(f"Error parsing base64 DOCX: {e}")
            return ""
    else:
        print("Unsupported document type.")
        return ""

def clean_extracted_text(text: str) -> str:
    """
    Optional: Basic cleaning to remove excessive whitespace or
    non-printable characters before sending to the LLM.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print(f"--- [Document Loader] Cleaned extracted text, total characters after cleaning: {sum(len(t) for t in lines)} ---")
    return "\n".join(lines)
