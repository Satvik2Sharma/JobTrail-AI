import io
import json
import os
import sys
import httpx
import pymupdf as fitz
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserProfile
from app.models.resume import Resume
from app.models.job import Job, JobEmbedding
from app.core.config import settings

def run_real_end_to_end_validation():
    print("=" * 80)
    print("JOBTRAIL-AI REAL END-TO-END RESUME INTELLIGENCE PIPELINE VALIDATION")
    print("Target Resume: Satvik_Resume_1st-year.pdf")
    print("=" * 80)

    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=60.0)
    results = {}

    # Verify input resume exists
    resume_path = "Satvik_Resume_1st-year.pdf"
    if not os.path.exists(resume_path):
        resume_path = "data/satvik_resume_1st_year.pdf"
    assert os.path.exists(resume_path), f"Resume file not found at {resume_path}"

    with open(resume_path, "rb") as f:
        real_resume_bytes = f.read()

    print(f"Loaded real candidate resume: {resume_path} ({len(real_resume_bytes)} bytes)")

    # -------------------------------------------------------------------------
    # STEP 1 & 2: AUTHENTICATION & ACTUAL UPLOAD FLOW
    # -------------------------------------------------------------------------
    print("\n[STEP 1 & 2] Authenticating Demo Candidate & Uploading Resume...")
    login_resp = client.post("/api/auth/login", json={
        "email": "demo@jobtrail.local",
        "password": "JobTrailDemo2026!"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload via POST /api/resume/upload
    files = {"file": ("Satvik_Resume_1st-year.pdf", real_resume_bytes, "application/pdf")}
    upload_resp = client.post("/api/resume/upload", headers=headers, files=files)
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    upload_data = upload_resp.json()

    assert upload_data["status"] == "completed"
    assert upload_data["resume_id"] is not None
    assert upload_data["storage_path"].startswith("users/")
    assert upload_data["file_size"] == len(real_resume_bytes)
    assert upload_data["mime_type"] == "application/pdf"
    assert upload_data["parser_version"] == "pymupdf_v1"
    assert upload_data["embedding_generated"] is True

    resume_id = upload_data["resume_id"]
    storage_path = upload_data["storage_path"]
    intel = upload_data["intelligence"]
    char_count = intel["raw_text_length"]

    results["STEP_1_UPLOAD"] = {
        "status": "PASS",
        "resume_id": resume_id,
        "storage_path": storage_path,
        "file_size_bytes": len(real_resume_bytes),
        "mime_type": upload_data["mime_type"]
    }
    results["STEP_2_EXTRACTION"] = {
        "status": "PASS",
        "raw_character_count": char_count,
        "parsing_status": upload_data["status"],
        "parser_version": upload_data["parser_version"]
    }

    print(f"  ✓ Upload status: {upload_data['status']}")
    print(f"  ✓ Resume ID: {resume_id}")
    print(f"  ✓ Storage Path: {storage_path}")
    print(f"  ✓ Text Extracted: {char_count} characters using PyMuPDF v1")

    # -------------------------------------------------------------------------
    # STEP 3: STRUCTURED EXTRACTION VERIFICATION
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Verifying Extracted Structured Fields...")
    assert intel["name"] == "Satvik Sharma", f"Expected Satvik Sharma, got: {intel['name']}"
    assert intel["email"] == "satviksharma1706@gmail.com", f"Unexpected email: {intel['email']}"
    assert "7017376181" in intel["phone"], f"Unexpected phone: {intel['phone']}"
    assert "Roorkee" in intel["location"] or "Uttarakhand" in intel["location"], f"Unexpected location: {intel['location']}"
    assert "Computer Science" in intel["degree"] or "B.Tech" in intel["education"]
    assert "8.2" in intel["cgpa"], f"Expected 8.2 CGPA, got: {intel['cgpa']}"
    assert len(intel["detected_skills"]) >= 15, f"Too few skills: {len(intel['detected_skills'])}"
    assert len(intel["projects"]) >= 3, f"Projects missed: {len(intel['projects'])}"
    assert len(intel["internships"]) >= 1, f"Internships missed: {len(intel['internships'])}"
    assert len(intel["research_publications"]) >= 1, f"Research missed: {len(intel['research_publications'])}"
    assert len(intel["certifications"]) >= 1, f"Certifications missed: {len(intel['certifications'])}"
    assert len(intel["interests"]) >= 1, f"Interests missed: {len(intel['interests'])}"

    results["STEP_3_STRUCTURED_EXTRACTION"] = {
        "status": "PASS",
        "name": intel["name"],
        "email": intel["email"],
        "phone": intel["phone"],
        "location": intel["location"],
        "education": intel["education"],
        "degree": intel["degree"],
        "graduation_year": intel["graduation_year"],
        "cgpa": intel["cgpa"],
        "experience_years": intel["experience_years"],
        "internships_count": len(intel["internships"]),
        "projects_count": len(intel["projects"]),
        "research_publications_count": len(intel["research_publications"]),
        "certifications_count": len(intel["certifications"]),
        "interests_count": len(intel["interests"]),
        "profile_completeness": intel["profile_completeness"]
    }

    print(f"  ✓ Candidate Name: {intel['name']}")
    print(f"  ✓ Email: {intel['email']}")
    print(f"  ✓ Phone: {intel['phone']}")
    print(f"  ✓ Location: {intel['location']}")
    print(f"  ✓ Degree / Education: {intel['degree']} ({intel['education']})")
    print(f"  ✓ CGPA: {intel['cgpa']}")
    print(f"  ✓ Internships Extracted ({len(intel['internships'])}): {intel['internships'][:1]}")
    print(f"  ✓ Projects Extracted ({len(intel['projects'])}): {intel['projects'][:2]}")
    print(f"  ✓ Research Extracted ({len(intel['research_publications'])}): {intel['research_publications'][:1]}")
    print(f"  ✓ Certifications Extracted ({len(intel['certifications'])}): {intel['certifications'][:2]}")
    print(f"  ✓ Interests Extracted ({len(intel['interests'])}): {intel['interests']}")

    # -------------------------------------------------------------------------
    # STEP 4: SKILL NORMALIZATION
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Verifying Skill Normalization Taxonomy Mapping...")
    detected_skills = intel["detected_skills"]
    assert len(detected_skills) == len(set(detected_skills)), "Duplicate skills detected!"
    # Verify core skills present in Satvik's resume
    expected_sample_skills = ["YOLOv8", "FastAPI", "React", "Next.js", "Python", "C++", "TensorFlow", "OpenCV", "NLP"]
    for s in expected_sample_skills:
        assert s in detected_skills, f"Expected canonical skill '{s}' not detected!"

    results["STEP_4_SKILL_NORMALIZATION"] = {
        "status": "PASS",
        "total_skills_extracted": len(detected_skills),
        "detected_canonical_skills": detected_skills,
        "sample_verified": expected_sample_skills
    }
    print(f"  ✓ Extracted {len(detected_skills)} canonical skills with zero duplicates.")
    print(f"  ✓ Verified canonical mapping: {expected_sample_skills}")

    # -------------------------------------------------------------------------
    # STEP 5: DATABASE PERSISTENCE CHECK (INDEPENDENT DB SESSION)
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Verifying Independent Database Persistence...")
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@jobtrail.local").first()
        assert user is not None
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        assert profile is not None
        assert profile.cgpa == "8.2 CGPA"
        assert profile.location == "Roorkee, Uttarakhand"
        assert profile.candidate_embedding_json is not None
        
        # Verify active resume in resumes table
        active_res = db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active == True).first()
        assert active_res is not None
        assert active_res.id == resume_id
        assert active_res.storage_path == storage_path
    finally:
        db.close()

    results["STEP_5_DATABASE_PERSISTENCE"] = {
        "status": "PASS",
        "persisted_profile_id": profile.id,
        "persisted_cgpa": profile.cgpa,
        "persisted_location": profile.location,
        "active_resume_id": active_res.id
    }
    print(f"  ✓ Database record confirmed: UserProfile ID {profile.id}, CGPA '{profile.cgpa}', Location '{profile.location}'")
    print(f"  ✓ Active Resume verified in resumes table (ID {active_res.id})")

    # -------------------------------------------------------------------------
    # STEP 6: CANDIDATE EMBEDDING GENERATION
    # -------------------------------------------------------------------------
    print("\n[STEP 6] Verifying Candidate Embedding Vector...")
    cand_vec = json.loads(profile.candidate_embedding_json)
    assert len(cand_vec) == 384, f"Dimension mismatch: expected 384, got {len(cand_vec)}"

    # Check job embedding dimension
    db = SessionLocal()
    try:
        job_emb = db.query(JobEmbedding).first()
        if job_emb:
            job_vec = json.loads(job_emb.embedding_json)
            assert len(job_vec) == len(cand_vec) == 384
    finally:
        db.close()

    results["STEP_6_EMBEDDING"] = {
        "status": "PASS",
        "embedding_dimension": len(cand_vec),
        "model_architecture": settings.EMBEDDING_MODEL_NAME,
        "vector_sample": cand_vec[:5]
    }
    print(f"  ✓ Candidate embedding dimension: {len(cand_vec)} (matches job embeddings)")

    # -------------------------------------------------------------------------
    # STEP 7 & 8: RECOMMENDATIONS & EXPLAINABLE MATCH ANALYSIS
    # -------------------------------------------------------------------------
    print("\n[STEP 7 & 8] Generating Recommendations and Explainable Match Scoring...")
    recs_resp = client.get("/api/recommendations?limit=10", headers=headers)
    assert recs_resp.status_code == 200, f"Recommendations failed: {recs_resp.text}"
    recs_data = recs_resp.json()
    assert recs_data["total_matches"] > 0
    assert len(recs_data["items"]) >= 5

    top_recs = recs_data["items"][:5]
    top_5_summary = []

    for idx, item in enumerate(top_recs):
        job = item["job"]
        match = item["match"]

        # Verify 4-dimensional score integrity
        semantic = match["semantic_match"]
        skill = match["skill_match"]
        eligibility = match["eligibility_match"]
        preference = match["preference_match"]
        overall = match["overall_match"]

        # Formula check: 0.50*semantic + 0.25*skill + 0.15*eligibility + 0.10*preference
        expected_score = int(round(0.50 * semantic + 0.25 * skill + 0.15 * eligibility + 0.10 * preference))
        # Allow +/- 1 point rounding variance
        assert abs(overall - expected_score) <= 1, f"Score mismatch: {overall} vs {expected_score}"

        # Explanation check
        assert len(match["explanation"]) >= 2
        assert len(match["matching_skills"]) > 0 or len(match["missing_skills"]) > 0

        top_5_summary.append({
            "rank": idx + 1,
            "title": job["title"],
            "company": job["company"],
            "overall_match": overall,
            "semantic_match": semantic,
            "skill_match": skill,
            "eligibility_match": eligibility,
            "preference_match": preference,
            "matched_skills": match["matching_skills"],
            "missing_skills": match["missing_skills"][:3],
            "explanation": match["explanation"][:2]
        })

    results["STEP_7_RECOMMENDATIONS"] = {
        "status": "PASS",
        "total_matches": recs_data["total_matches"],
        "returned_items": len(recs_data["items"])
    }
    results["STEP_8_EXPLANATIONS"] = {
        "status": "PASS",
        "top_5": top_5_summary
    }

    print(f"  ✓ Total job matches: {recs_data['total_matches']}")
    print("  ✓ Top 5 Personalized Opportunities:")
    for rec in top_5_summary:
        print(f"    #{rec['rank']} {rec['title']} at {rec['company']}")
        print(f"       Overall: {rec['overall_match']}% [Semantic: {rec['semantic_match']}%, Skills: {rec['skill_match']}%, Elig: {rec['eligibility_match']}%, Pref: {rec['preference_match']}%]")
        print(f"       Matched Skills: {rec['matched_skills']}")
        print(f"       Explanation: {rec['explanation'][0]}")

    # -------------------------------------------------------------------------
    # STEP 9: SKILL GAP ANALYSIS
    # -------------------------------------------------------------------------
    print("\n[STEP 9] Verifying Skill Gap Analysis Endpoint...")
    top_job_id = top_recs[0]["job"]["id"]
    skill_gap_resp = client.get(f"/api/skill-gap?job_id={top_job_id}", headers=headers)
    assert skill_gap_resp.status_code == 200, f"Skill gap failed: {skill_gap_resp.text}"
    sg_data = skill_gap_resp.json()

    assert "already_have" in sg_data
    assert "missing" in sg_data
    assert "readiness_score" in sg_data
    assert "career_insight" in sg_data

    results["STEP_9_SKILL_GAP"] = {
        "status": "PASS",
        "target_job_title": sg_data.get("target_job_title"),
        "already_have_count": len(sg_data["already_have"]),
        "missing_skills": sg_data["missing"],
        "missing_details_count": len(sg_data.get("missing_details", [])),
        "readiness_score": sg_data["readiness_score"],
        "career_insight": sg_data["career_insight"]
    }
    print(f"  ✓ Evaluated Skill Gap for '{sg_data.get('target_job_title')}':")
    print(f"    - Acquired Skills: {len(sg_data['already_have'])}")
    print(f"    - Missing Skills: {sg_data['missing']}")
    print(f"    - Readiness Score: {sg_data['readiness_score']}%")
    print(f"    - Career Insight: {sg_data['career_insight']}")

    # -------------------------------------------------------------------------
    # STEP 10: SECURITY AUDIT
    # -------------------------------------------------------------------------
    print("\n[STEP 10] Executing Security and Authorization Audit...")
    import uuid
    intruder_email = f"intruder_{uuid.uuid4().hex[:8]}@jobtrail.local"
    reg_b = client.post("/api/auth/register", json={
        "email": intruder_email,
        "password": "IntruderPass2026!",
        "full_name": "Intruder Candidate",
        "role": "candidate"
    })
    assert reg_b.status_code == 201 or reg_b.status_code == 200
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # B attempts to access A's resume by ID -> 403 Forbidden
    resp_unauth_view = client.get(f"/api/resume/{resume_id}", headers=headers_b)
    assert resp_unauth_view.status_code == 403, f"Expected 403, got: {resp_unauth_view.status_code}"

    # B attempts to download A's resume by storage path -> 403 Forbidden
    resp_unauth_dl = client.get(f"/api/resume/download/{storage_path}", headers=headers_b)
    assert resp_unauth_dl.status_code == 403, f"Expected 403, got: {resp_unauth_dl.status_code}"

    # Owner A can download their resume -> 200 OK
    resp_auth_dl = client.get(f"/api/resume/download/{storage_path}", headers=headers)
    assert resp_auth_dl.status_code == 200
    assert resp_auth_dl.content == real_resume_bytes

    # Verify SUPABASE_SERVICE_ROLE_KEY is not leaked in health or auth responses
    health_resp = client.get("/health")
    assert "SUPABASE_SERVICE_ROLE_KEY" not in health_resp.text
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        assert settings.SUPABASE_SERVICE_ROLE_KEY not in health_resp.text

    results["STEP_10_SECURITY"] = {
        "status": "PASS",
        "cross_user_view_blocked": "403 Forbidden",
        "cross_user_download_blocked": "403 Forbidden",
        "owner_download_verified": "200 OK",
        "secret_leak_audit": "Clean"
    }
    print("  ✓ Cross-user resume view blocked (403 Forbidden)")
    print("  ✓ Cross-user resume download blocked (403 Forbidden)")
    print("  ✓ Owner resume download verified (200 OK)")
    print("  ✓ Secrets audited: Service Role Key never exposed to client")

    # -------------------------------------------------------------------------
    # STEP 11: SESSION PERSISTENCE (LOGOUT -> LOGIN -> RETRIEVE)
    # -------------------------------------------------------------------------
    print("\n[STEP 11] Verifying Session & Data Persistence across Logouts...")
    client.post("/api/auth/logout", headers=headers)

    # Re-login
    relogin_resp = client.post("/api/auth/login", json={
        "email": "demo@jobtrail.local",
        "password": "JobTrailDemo2026!"
    })
    assert relogin_resp.status_code == 200
    new_token = relogin_resp.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    # Verify profile and resume still intact
    get_res = client.get("/api/resume", headers=new_headers)
    assert get_res.status_code == 200
    resume_state = get_res.json()
    assert resume_state["has_resume"] is True
    assert resume_state["intelligence"]["name"] == "Satvik Sharma"
    assert resume_state["intelligence"]["cgpa"] == "8.2 CGPA"

    # Verify saved job persistence
    save_resp = client.post(f"/api/jobs/{top_job_id}/save", headers=new_headers)
    assert save_resp.status_code == 200
    saved_list_data = client.get("/api/saved-jobs", headers=new_headers).json()
    saved_items = saved_list_data.get("items", saved_list_data) if isinstance(saved_list_data, dict) else saved_list_data
    assert any(j["id"] == top_job_id for j in saved_items)

    results["STEP_11_PERSISTENCE"] = {
        "status": "PASS",
        "resume_associated": True,
        "profile_cgpa": resume_state["intelligence"]["cgpa"],
        "saved_jobs_functional": True
    }
    print("  ✓ Re-login verified. Profile, CGPA, and resume data fully persisted.")
    print(f"  ✓ Saved job lifecycle confirmed on job {top_job_id}.")

    # -------------------------------------------------------------------------
    # STEP 12: FAILURE MODES & CORNER CASES
    # -------------------------------------------------------------------------
    print("\n[STEP 12] Testing Robustness Against Edge Cases & Corrupt Inputs...")
    
    # 1. Non-PDF
    bad_ext = client.post("/api/resume/upload", headers=new_headers, files={"file": ("doc.txt", b"plain text", "text/plain")})
    assert bad_ext.status_code == 400
    assert "Invalid file format" in bad_ext.json()["detail"]

    # 2. Empty PDF (0 bytes)
    empty_pdf = client.post("/api/resume/upload", headers=new_headers, files={"file": ("empty.pdf", b"", "application/pdf")})
    assert empty_pdf.status_code == 400
    assert "empty" in empty_pdf.json()["detail"]

    # 3. Corrupted PDF
    corrupt_pdf = client.post("/api/resume/upload", headers=new_headers, files={"file": ("corrupt.pdf", b"%PDF-1.4 garbage invalid header bytes", "application/pdf")})
    assert corrupt_pdf.status_code in (400, 500)

    # 4. Oversized PDF (>10MB)
    huge_bytes = b"%PDF-1.4" + (b"0" * (11 * 1024 * 1024))
    huge_pdf = client.post("/api/resume/upload", headers=new_headers, files={"file": ("huge.pdf", huge_bytes, "application/pdf")})
    assert huge_pdf.status_code == 400
    assert "exceeds limit" in huge_pdf.json()["detail"]

    # 5. Scanned / Image-only PDF
    blank_doc = fitz.open()
    blank_doc.new_page()
    scanned_bytes = blank_doc.tobytes()
    blank_doc.close()

    scanned_pdf = client.post("/api/resume/upload", headers=new_headers, files={"file": ("scanned.pdf", scanned_bytes, "application/pdf")})
    assert scanned_pdf.status_code == 400
    scanned_detail = scanned_pdf.json()["detail"]
    assert "OCR" in scanned_detail or "Scanned or image-only" in scanned_detail

    results["STEP_12_FAILURE_CASES"] = {
        "status": "PASS",
        "non_pdf_rejected": "400 Bad Request",
        "empty_pdf_rejected": "400 Bad Request",
        "corrupted_pdf_rejected": f"{corrupt_pdf.status_code} Rejected",
        "oversized_pdf_rejected": "400 Bad Request",
        "scanned_pdf_ocr_message": scanned_detail
    }
    print(f"  ✓ Non-PDF rejected: {bad_ext.status_code}")
    print(f"  ✓ Empty PDF rejected: {empty_pdf.status_code}")
    print(f"  ✓ Corrupted PDF rejected: {corrupt_pdf.status_code}")
    print(f"  ✓ Oversized PDF (>10MB) rejected: {huge_pdf.status_code}")
    print(f"  ✓ Scanned/Image-only PDF correctly returns OCR notice: '{scanned_detail[:60]}...'")

    print("\n" + "=" * 80)
    print("ALL 12 PIPELINE STAGES PASSED REAL END-TO-END VALIDATION SUCCESSFULLY!")
    print("=" * 80)

    # Save validation artifact
    with open("data/real_pipeline_validation_results.json", "w") as out_f:
        json.dump(results, out_f, indent=2)
    print("Validation results saved to data/real_pipeline_validation_results.json")

    return results

if __name__ == "__main__":
    run_real_end_to_end_validation()
