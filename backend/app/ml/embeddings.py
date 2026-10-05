import numpy as np
from typing import List, Optional, Union
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings

class EmbeddingService:
    """
    Singleton service managing SentenceTransformer model for JobTrail-AI.
    Ensures model weights are loaded once in memory and reused across all requests.
    """
    _instance: Optional["EmbeddingService"] = None

    def __init__(self):
        self._model = None
        self.model_name = settings.EMBEDDING_MODEL_NAME

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            # Lazy load on first access
            from sentence_transformers import SentenceTransformer
            print(f"[EmbeddingService] Loading SentenceTransformer: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print("[EmbeddingService] Model loaded successfully.")
        return self._model

    def encode_text(self, text: str) -> np.ndarray:
        """Encode single string into a 1D float vector."""
        if not text:
            text = "general software engineering"
        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return np.asarray(embedding, dtype=np.float32)

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode list of strings into 2D numpy array [N, D]."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)

    def encode_candidate(self, candidate_text: str) -> np.ndarray:
        return self.encode_text(candidate_text)

    def encode_job(self, job_text: str) -> np.ndarray:
        return self.encode_text(job_text)

    def calculate_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two 1D or 2D vectors.
        Returns raw float bounded in [-1.0, 1.0], clamped to [0.0, 1.0].
        """
        a = np.asarray(vec_a, dtype=np.float32).reshape(1, -1)
        b = np.asarray(vec_b, dtype=np.float32).reshape(1, -1)
        cos_sim = float(cosine_similarity(a, b)[0][0])
        # Clamp to realistic positive similarity [0.0, 1.0]
        return max(0.0, min(1.0, cos_sim))

    def build_candidate_representation(
        self,
        degree: Optional[str] = None,
        field: Optional[str] = None,
        education: Optional[str] = None,
        skills: Optional[List[str]] = None,
        experience_years: float = 0.0,
        interests: Optional[str] = None,
        resume_summary: Optional[str] = None
    ) -> str:
        """
        Builds deterministic textual profile representation for sentence embedding.
        """
        parts = ["Candidate Profile:"]
        edu_part = []
        if degree:
            edu_part.append(degree)
        elif education:
            edu_part.append(education)
        if field and (not degree or field.lower() not in degree.lower()):
            edu_part.append(f"in {field}")
        
        if edu_part:
            parts.append(f"Education: {' '.join(edu_part)}.")
        
        if experience_years > 0:
            parts.append(f"Experience: {experience_years:.1f} years in tech.")
        else:
            parts.append("Experience: Student / Entry-level.")

        if skills:
            parts.append(f"Skills: {', '.join(skills)}.")

        if interests:
            parts.append(f"Interests & Career Focus: {interests}.")

        if resume_summary:
            parts.append(f"Background: {resume_summary[:300]}.")

        return " ".join(parts)

    def build_job_representation(
        self,
        title: str,
        category: str,
        skills: List[str],
        description: str,
        requirements: Optional[str] = None,
        experience_level: Optional[str] = None
    ) -> str:
        """
        Builds standardized job representation text for embedding.
        """
        parts = [
            f"Job Title: {title}.",
            f"Category: {category}.",
            f"Experience: {experience_level or 'Any'}.",
            f"Required Skills: {', '.join(skills)}.",
            f"Description: {description[:350]}."
        ]
        if requirements:
            parts.append(f"Requirements: {requirements[:200]}.")
        return " ".join(parts)

embedding_service = EmbeddingService.get_instance()
