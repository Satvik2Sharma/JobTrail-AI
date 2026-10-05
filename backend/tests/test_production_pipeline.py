import io
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile
from app.models.resume import Resume
from app.storage.local_storage import LocalStorageService
from app.storage.supabase_storage import SupabaseStorageService
from app.core.config import settings

def test_storage_abstraction_local(tmp_path):
    storage = LocalStorageService(base_dir=str(tmp_path))
    test_path = "users/1/resumes/10/resume.pdf"
    content = b"%PDF-1.4 test resume content"

    # Upload
    saved_path = storage.upload_file(content, test_path, "application/pdf")
    assert saved_path == test_path
    assert storage.file_exists(test_path)

    # Download
    downloaded = storage.download_file(test_path)
    assert downloaded == content

    # URL
    url = storage.get_file_url(test_path)
    assert "users/1/resumes/10/resume.pdf" in url

    # Path traversal protection
    with pytest.raises(ValueError, match="Path traversal"):
        storage.upload_file(content, "../../../evil.txt")

    # Delete
    deleted = storage.delete_file(test_path)
    assert deleted is True
    assert not storage.file_exists(test_path)

def test_resume_upload_full_production_pipeline(client: TestClient, candidate_headers: dict, db_session: Session):
    with open("data/sample_resume.pdf", "rb") as f:
        file_bytes = f.read()

    resp = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("satvik_sharma.pdf", file_bytes, "application/pdf")}
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "completed"
    assert data["resume_id"] is not None
    assert "users/" in data["storage_path"]
    assert "resumes/" in data["storage_path"]
    assert data["file_size"] == len(file_bytes)
    assert data["mime_type"] == "application/pdf"
    assert data["parser_version"] == "pymupdf_v1"
    assert data["embedding_generated"] is True

    # Check structured intelligence
    intel = data["intelligence"]
    assert intel["name"] == "Satvik Sharma"
    assert intel["email"] == "satvik.sharma@example.com"
    assert "San Francisco" in intel["location"]
    assert "3.85" in intel["cgpa"]
    assert len(intel["detected_skills"]) >= 15
    assert len(intel["internships"]) >= 1

    # Check UserProfile persistence
    user = db_session.query(User).filter(User.email == "test_candidate@jobtrail.local").first()
    profile = db_session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    assert profile is not None
    assert profile.cgpa == "3.85 / 4.0"
    assert profile.location == "San Francisco, CA"
    assert profile.candidate_embedding_json is not None
    cand_vec = json.loads(profile.candidate_embedding_json)
    assert len(cand_vec) == 384 # MiniLM embedding dimension

    # Check Resume record in database
    resume_rec = db_session.query(Resume).filter(Resume.id == data["resume_id"]).first()
    assert resume_rec is not None
    assert resume_rec.user_id == user.id
    assert resume_rec.is_active is True
    assert resume_rec.parsing_status == "completed"

def test_duplicate_resume_replacement(client: TestClient, candidate_headers: dict, db_session: Session):
    user = db_session.query(User).filter(User.email == "test_candidate@jobtrail.local").first()
    with open("data/sample_resume.pdf", "rb") as f:
        file_bytes = f.read()

    # Upload first time
    resp1 = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("resume_v1.pdf", file_bytes, "application/pdf")}
    )
    assert resp1.status_code == 200
    res1_id = resp1.json()["resume_id"]

    # Upload second time (replacement)
    resp2 = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("resume_v2.pdf", file_bytes, "application/pdf")}
    )
    assert resp2.status_code == 200
    res2_id = resp2.json()["resume_id"]
    assert res1_id != res2_id

    # Verify resume states
    res1 = db_session.query(Resume).filter(Resume.id == res1_id).first()
    res2 = db_session.query(Resume).filter(Resume.id == res2_id).first()

    assert res1.is_active is False # Old resume marked inactive
    assert res2.is_active is True  # New resume marked active

    # Verify no duplicate UserProfile records
    profiles_count = db_session.query(UserProfile).filter(UserProfile.user_id == user.id).count()
    assert profiles_count == 1

def test_resume_ownership_authorization(client: TestClient, candidate_headers: dict, db_session: Session):
    # Candidate uploads resume
    with open("data/sample_resume.pdf", "rb") as f:
        file_bytes = f.read()

    resp = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("my_resume.pdf", file_bytes, "application/pdf")}
    )
    resume_id = resp.json()["resume_id"]
    storage_path = resp.json()["storage_path"]

    # Register second user (Candidate B)
    reg_b = client.post("/api/auth/register", json={
        "email": "intruder@jobtrail.local",
        "password": "Password123!",
        "full_name": "Intruder Candidate",
        "role": "candidate"
    })
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Candidate B attempts to view Candidate A's resume by ID -> 403 Forbidden
    resp_unauth_view = client.get(f"/api/resume/{resume_id}", headers=headers_b)
    assert resp_unauth_view.status_code == 403

    # Candidate B attempts to download Candidate A's resume -> 403 Forbidden
    resp_unauth_dl = client.get(f"/api/resume/download/{storage_path}", headers=headers_b)
    assert resp_unauth_dl.status_code == 403

    # Candidate A can download their own resume -> 200 OK
    resp_auth_dl = client.get(f"/api/resume/download/{storage_path}", headers=candidate_headers)
    assert resp_auth_dl.status_code == 200
    assert resp_auth_dl.content == file_bytes

def test_resume_error_handling_invalid_and_oversized_pdf(client: TestClient, candidate_headers: dict):
    # Reject non-PDF file
    resp_txt = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("resume.txt", b"plain text", "text/plain")}
    )
    assert resp_txt.status_code == 400
    assert "Invalid file format" in resp_txt.json()["detail"]

    # Reject empty PDF
    resp_empty = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert resp_empty.status_code == 400

    # Reject corrupt header
    resp_corrupt = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("corrupt.pdf", b"NOT_A_PDF_CONTENT", "application/pdf")}
    )
    assert resp_corrupt.status_code == 400
    assert "Corrupted or invalid PDF" in resp_corrupt.json()["detail"]

    # Reject oversized file (>10MB)
    huge_bytes = b"%PDF-1.4" + (b"0" * (11 * 1024 * 1024))
    resp_huge = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("huge.pdf", huge_bytes, "application/pdf")}
    )
    assert resp_huge.status_code == 400
    assert "exceeds limit" in resp_huge.json()["detail"]

def test_resume_error_handling_scanned_pdf(client: TestClient, candidate_headers: dict):
    import pymupdf as fitz
    # Create empty valid PDF without text (simulating image or scanned PDF)
    doc = fitz.open()
    doc.new_page() # blank page
    scanned_bytes = doc.tobytes()
    doc.close()

    resp = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("scanned_resume.pdf", scanned_bytes, "application/pdf")}
    )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert "OCR" in detail or "Scanned or image-only" in detail

def test_health_check_dual_endpoints(client: TestClient):
    # Test GET /health
    resp1 = client.get("/health")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "healthy"
    assert data1["database"]["status"] == "connected"
    assert data1["database"]["ready"] is True

    # Test GET /api/health
    resp2 = client.get("/api/health")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "healthy"
    assert data2["database"]["status"] == "connected"
    assert data2["database"]["ready"] is True
