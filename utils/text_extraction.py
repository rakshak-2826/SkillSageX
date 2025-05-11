import os
import fitz  # PyMuPDF
import docx2txt
from utils.config import logger

def extract_text(file_path: str) -> str:
    """
    Extracts raw text content from supported file formats:
    - PDF (.pdf)
    - Word (.docx)
    - Plain text (.txt)

    Returns empty string on failure or unsupported type.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            return ' '.join(page.get_text() for page in doc)

        elif ext == ".docx":
            return docx2txt.process(file_path)

        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            raise ValueError("Unsupported file format")

    except Exception as e:
        logger.error(f"❌ Failed to extract text from {file_path}: {str(e)}")
        return ""
