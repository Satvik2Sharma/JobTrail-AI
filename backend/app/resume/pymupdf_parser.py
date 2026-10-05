import os
from pathlib import Path
from typing import Union
from app.resume.parser_base import BaseResumeParser

class PyMuPDFResumeParser(BaseResumeParser):
    """
    Fast and robust PDF text extractor using PyMuPDF (fitz).
    Handles multi-column layouts, clean line endings, in-memory bytes or disk paths,
    and detects scanned/corrupted PDFs accurately.
    """

    def extract_text(self, file_input: Union[str, Path, bytes]) -> str:
        try:
            import pymupdf as fitz
        except ImportError:
            try:
                import fitz
            except ImportError:
                raise RuntimeError("PyMuPDF is not installed.")

        doc = None
        extracted_pages = []
        try:
            if isinstance(file_input, bytes):
                if len(file_input) == 0:
                    raise ValueError("Uploaded PDF file is empty (0 bytes).")
                doc = fitz.open(stream=file_input, filetype="pdf")
            elif isinstance(file_input, (str, Path)):
                file_path = str(file_input)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Resume file not found at: {file_path}")
                if os.path.getsize(file_path) == 0:
                    raise ValueError("Resume file is empty (0 bytes).")
                doc = fitz.open(file_path)
            else:
                raise ValueError("Invalid file input: must be file path or bytes.")

            if doc.page_count == 0:
                raise ValueError("PDF document is empty (0 pages).")

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                # Extract text with layout sorting
                text = page.get_text("text", sort=True)
                if text and text.strip():
                    extracted_pages.append(text.strip())

        except (fitz.FileDataError, fitz.EmptyFileError) as e:
            raise ValueError(f"Corrupted or invalid PDF file: {str(e)}")
        except Exception as e:
            if isinstance(e, (ValueError, FileNotFoundError)):
                raise
            raise ValueError(f"Failed to parse PDF with PyMuPDF: {str(e)}")
        finally:
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass

        full_text = "\n\n".join(extracted_pages)
        # Scanned or image-only PDFs yield 0 or practically 0 characters
        if not full_text.strip() or len(full_text.strip()) < 20:
            raise ValueError(
                "No extractable text found in PDF. Scanned or image-only PDFs require OCR processing and are not supported yet."
            )

        return full_text
