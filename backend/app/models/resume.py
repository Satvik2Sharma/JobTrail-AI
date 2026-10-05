from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), default="application/pdf")
    file_size = Column(Integer, nullable=False)
    parsing_status = Column(String(50), default="completed", index=True) # pending, completed, failed
    parser_version = Column(String(50), default="pymupdf_v1")
    is_active = Column(Boolean, default=True, index=True)
    extracted_data = Column(Text, nullable=True) # Structured JSON string (CGPA, projects, certifications, etc.)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="resumes")
