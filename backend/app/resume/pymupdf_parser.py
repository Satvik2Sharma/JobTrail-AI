import os
from app.resume.parser_base import BaseResumeParser

class PyMuPDFResumeParser(BaseResumeParser):
    """
    Fast and robust PDF text extractor using PyMuPDF (fitz).
    Handles multi-column layouts, clean line endings, and malformed files.
    """

    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found at: {file_path}")

        try:
            import pymupdf as fitz  # Modern PyMuPDF import
        except ImportError:
            try:
                import fitz
            except ImportError:
                raise RuntimeError("PyMuPDF is not installed.")

        extracted_pages = []
        try:
            with fitz.open(file_path) as doc:
                if doc.page_count == 0:
                    raise ValueError("PDF document is empty (0 pages).")

                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    # Extract text with block sorting to preserve column layout flow
                    text = page.get_text("text", sort=True)
                    if text.strip():
                        extracted_pages.append(text.strip())

        except Exception as e:
            raise ValueError(f"Failed to parse PDF with PyMuPDF: {str(e)}")

        full_text = "\n\n".join(extracted_pages)
        if not full_text.strip():
            raise ValueError("No extractable text found in PDF. Scanned or image-only PDFs are not supported yet.")

        return full_text
