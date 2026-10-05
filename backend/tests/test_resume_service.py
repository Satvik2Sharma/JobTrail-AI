import pytest
import os
from pathlib import Path
from app.resume.resume_service import resume_service
from app.resume.pymupdf_parser import PyMuPDFResumeParser

def test_resume_service_extract_text_from_sample():
    sample_path = "data/sample_resume.pdf"
    assert os.path.exists(sample_path)
    
    text = resume_service.extract_text_from_file(sample_path)
    assert len(text) > 100
    assert "Alex Chen" in text
    assert "Computer Science" in text
    assert "Python" in text

def test_resume_service_intelligence_parsing():
    sample_path = "data/sample_resume.pdf"
    raw_text = resume_service.extract_text_from_file(sample_path)
    data = resume_service.parse_resume_intelligence(raw_text)

    assert data["name"] == "Alex Chen"
    assert data["email"] == "alex.chen@example.com"
    assert "555" in data["phone"]
    assert "Computer Science" in data["field_of_study"]
    assert data["graduation_year"] == 2025
    assert len(data["detected_skills"]) >= 15
    assert "Python" in data["detected_skills"]
    assert "FastAPI" in data["detected_skills"]
    assert "Machine Learning" in data["detected_skills"]
    assert data["profile_completeness"] >= 80

def test_resume_service_completeness_calculation():
    # Complete candidate
    full_score = resume_service.calculate_completeness(
        name="Alex Chen",
        email="alex@example.com",
        phone="+1 555-1234",
        degree="B.Tech Computer Science",
        field="Computer Science",
        skills=["Python", "FastAPI", "React", "Docker", "SQL"],
        experience_years=1.0,
        projects=["Recommendation System", "CV pipeline"]
    )
    assert full_score == 100

    # Incomplete candidate (only name and email)
    partial_score = resume_service.calculate_completeness(
        name="John Doe",
        email="john@example.com",
        phone=None,
        degree=None,
        field=None,
        skills=[],
        experience_years=0.0,
        projects=[]
    )
    assert partial_score == 25 # 10 (name) + 15 (email)

def test_resume_service_file_validation():
    # Reject non-PDF
    with pytest.raises(ValueError, match="Only PDF"):
        resume_service.save_uploaded_file(b"some content", "resume.docx")

    # Reject oversized file
    oversized_bytes = b"0" * (11 * 1024 * 1024)
    with pytest.raises(ValueError, match="exceeds limit"):
        resume_service.save_uploaded_file(oversized_bytes, "huge.pdf")
