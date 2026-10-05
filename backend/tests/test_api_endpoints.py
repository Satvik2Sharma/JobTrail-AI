import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_auth_registration_and_login(client: TestClient):
    # Register new user
    reg_resp = client.post("/api/auth/register", json={
        "email": "new_user@jobtrail.local",
        "password": "Password123!",
        "full_name": "New Candidate",
        "role": "candidate"
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "new_user@jobtrail.local"

    # Login with newly created user
    login_resp = client.post("/api/auth/login", json={
        "email": "new_user@jobtrail.local",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # Verify /me endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "new_user@jobtrail.local"

def test_auth_login_invalid_password(client: TestClient):
    resp = client.post("/api/auth/login", json={
        "email": "test_candidate@jobtrail.local",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401

def test_candidate_profile_operations(client: TestClient, candidate_headers: dict):
    # Get profile
    get_resp = client.get("/api/profile", headers=candidate_headers)
    assert get_resp.status_code == 200
    p_data = get_resp.json()
    assert p_data["full_name"] == "Alex Chen"
    assert p_data["profile_completeness"] > 50

    # Update profile
    put_resp = client.put("/api/profile", headers=candidate_headers, json={
        "location": "Oakland, CA",
        "remote_preference": "remote",
        "experience_years": 1.0
    })
    assert put_resp.status_code == 200
    assert put_resp.json()["location"] == "Oakland, CA"
    assert put_resp.json()["remote_preference"] == "remote"

    # Add a skill
    add_sk_resp = client.post("/api/profile/skills", headers=candidate_headers, json={
        "name": "Docker",
        "proficiency": "intermediate"
    })
    assert add_sk_resp.status_code == 200
    assert add_sk_resp.json()["name"] == "Docker"

    # Remove skill
    del_sk_resp = client.delete("/api/profile/skills/Docker", headers=candidate_headers)
    assert del_sk_resp.status_code == 200

def test_resume_upload_and_extraction(client: TestClient, candidate_headers: dict):
    with open("data/sample_resume.pdf", "rb") as f:
        file_bytes = f.read()

    resp = client.post(
        "/api/resume/upload",
        headers=candidate_headers,
        files={"file": ("sample_resume.pdf", file_bytes, "application/pdf")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["skills_detected_count"] > 10

    # Verify GET /resume
    get_res = client.get("/api/resume", headers=candidate_headers)
    assert get_res.status_code == 200
    assert get_res.json()["has_resume"] is True

def test_jobs_list_and_filters(client: TestClient, candidate_headers: dict):
    # List all jobs
    resp = client.get("/api/jobs", headers=candidate_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    # Filter by remote
    resp_remote = client.get("/api/jobs?remote=true", headers=candidate_headers)
    assert resp_remote.status_code == 200
    items = resp_remote.json()["items"]
    assert all(j["remote"] is True for j in items)

    # Get single job by ID
    first_id = data["items"][0]["id"]
    job_resp = client.get(f"/api/jobs/{first_id}", headers=candidate_headers)
    assert job_resp.status_code == 200
    assert job_resp.json()["id"] == first_id

def test_recommendations_and_explainable_match(client: TestClient, candidate_headers: dict):
    recs_resp = client.get("/api/recommendations", headers=candidate_headers)
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert recs["total_matches"] >= 3
    first_item = recs["items"][0]
    assert "job" in first_item
    assert "match" in first_item

    # Verify explainable match breakdown contract
    match = first_item["match"]
    assert 0 <= match["overall_match"] <= 100
    assert 0 <= match["semantic_match"] <= 100
    assert 0 <= match["skill_match"] <= 100
    assert 0 <= match["eligibility_match"] <= 100
    assert 0 <= match["preference_match"] <= 100
    assert isinstance(match["matching_skills"], list)
    assert isinstance(match["missing_skills"], list)
    assert isinstance(match["explanation"], list)
    assert len(match["explanation"]) > 0

    # Specific job match
    job_id = first_item["job"]["id"]
    match_detail_resp = client.get(f"/api/jobs/{job_id}/match", headers=candidate_headers)
    assert match_detail_resp.status_code == 200
    assert match_detail_resp.json()["job_id"] == job_id

def test_skill_gap_analysis(client: TestClient, candidate_headers: dict):
    # Aggregate skill gap across top recommendations
    agg_resp = client.get("/api/skill-gap", headers=candidate_headers)
    assert agg_resp.status_code == 200
    agg_data = agg_resp.json()
    assert "already_have" in agg_data
    assert "missing" in agg_data
    assert "career_insight" in agg_data
    assert "readiness_score" in agg_data

    # Single job skill gap
    jobs_resp = client.get("/api/jobs", headers=candidate_headers)
    first_id = jobs_resp.json()["items"][0]["id"]
    job_gap_resp = client.get(f"/api/skill-gap?job_id={first_id}", headers=candidate_headers)
    assert job_gap_resp.status_code == 200
    assert job_gap_resp.json()["target_job_id"] == first_id

def test_saved_jobs_lifecycle(client: TestClient, candidate_headers: dict):
    jobs_resp = client.get("/api/jobs", headers=candidate_headers)
    job_id = jobs_resp.json()["items"][0]["id"]

    # Save
    save_resp = client.post(f"/api/jobs/{job_id}/save", headers=candidate_headers)
    assert save_resp.status_code == 200
    assert save_resp.json()["saved"] is True

    # Check saved list
    saved_list = client.get("/api/saved-jobs", headers=candidate_headers)
    assert saved_list.status_code == 200
    saved_ids = [j["id"] for j in saved_list.json()["items"]]
    assert job_id in saved_ids

    # Unsave
    unsave_resp = client.delete(f"/api/jobs/{job_id}/save", headers=candidate_headers)
    assert unsave_resp.status_code == 200
    assert unsave_resp.json()["saved"] is False

def test_application_lifecycle(client: TestClient, candidate_headers: dict):
    jobs_resp = client.get("/api/jobs", headers=candidate_headers)
    job_id = jobs_resp.json()["items"][0]["id"]

    # Apply
    apply_resp = client.post(
        f"/api/jobs/{job_id}/apply",
        headers=candidate_headers,
        json={"notes": "Excited for this role!"}
    )
    assert apply_resp.status_code == 200
    app_data = apply_resp.json()
    app_id = app_data["id"]
    assert app_data["status"] == "applied"
    assert app_data["job_id"] == job_id

    # List applications
    apps_list = client.get("/api/applications", headers=candidate_headers)
    assert apps_list.status_code == 200
    assert any(a["id"] == app_id for a in apps_list.json())

    # Update status to interview
    update_resp = client.put(
        f"/api/applications/{app_id}",
        headers=candidate_headers,
        json={"status": "interview", "notes": "Technical round scheduled"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "interview"

def test_cannot_modify_other_user_application(client: TestClient, candidate_headers: dict):
    # Candidate A applies to a job
    jobs_resp = client.get("/api/jobs", headers=candidate_headers)
    job_id = jobs_resp.json()["items"][0]["id"]
    apply_resp = client.post(f"/api/jobs/{job_id}/apply", headers=candidate_headers, json={"notes": "User A"})
    app_id = apply_resp.json()["id"]

    # Register Candidate B
    reg_b = client.post("/api/auth/register", json={
        "email": "intruder@jobtrail.local",
        "password": "Password123!",
        "full_name": "Intruder User"
    })
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Candidate B attempts to modify Candidate A's application
    malicious_resp = client.put(
        f"/api/applications/{app_id}",
        headers=headers_b,
        json={"status": "selected", "notes": "Hacked status"}
    )
    assert malicious_resp.status_code == 403
    assert "permission" in malicious_resp.json()["detail"].lower()

def test_semantic_search_endpoint(client: TestClient):
    search_resp = client.get("/api/search?q=machine+learning+python+internship")
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert data["total_matches"] >= 1
    assert "items" in data
    # Highest relevance should be the ML role
    top_hit = data["items"][0]
    assert "Machine Learning" in top_hit["job"]["title"] or "ML" in top_hit["job"]["title"]

def test_recruiter_endpoints(client: TestClient, recruiter_headers: dict):
    # Recruiter creates new job
    new_job_resp = client.post(
        "/api/recruiter/jobs",
        headers=recruiter_headers,
        json={
            "title": "Autonomous AI Agent Developer",
            "company": "DeepFlow AI",
            "location": "Remote",
            "remote": True,
            "employment_type": "Full-time",
            "experience_level": "0-2 years",
            "education_requirement": "B.Tech/B.E. in CS or related field",
            "category": "Data Science & AI",
            "description": "Build next-generation autonomous AI agents and evaluation pipelines using Python and FastAPI.",
            "skills": ["Python", "FastAPI", "Machine Learning", "Docker"]
        }
    )
    assert new_job_resp.status_code == 201
    created_job = new_job_resp.json()
    created_id = created_job["id"]

    # Rank candidates for this new job
    rank_resp = client.get(f"/api/recruiter/jobs/{created_id}/candidates", headers=recruiter_headers)
    assert rank_resp.status_code == 200
    rankings = rank_resp.json()
    assert len(rankings) >= 1
    assert rankings[0]["candidate_email"] == "test_candidate@jobtrail.local"
    assert rankings[0]["match"]["overall_match"] > 70
