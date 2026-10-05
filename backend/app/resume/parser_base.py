from abc import ABC, abstractmethod

class BaseResumeParser(ABC):
    """
    Abstract Base Class for resume document parsers.
    Allows swappable implementations (PyMuPDF, Docling, pdfminer, etc.).
    """

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text content from the specified document.
        Raises ValueError or IOError if parsing fails.
        """
        pass
