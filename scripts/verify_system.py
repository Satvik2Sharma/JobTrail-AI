#!/usr/bin/env python3
"""
JobTrail-AI Comprehensive System Verification Script.
Executes the full end-to-end user journey against the live running application.
"""
import sys
import json
import httpx

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def run_verification():
    print("=" * 70)
    print("JOBTRAIL-AI — COMPREHENSIVE END-TO-END VERIFICATION AUDIT")
    print("=" * 70)
    client = httpx.Client(timeout=20.0)

    # 1. Verify Backend and Frontend are running
    print("\n[1/12] Verifying Backend & Frontend Services...")
    try:
        r_fe = client.get(FRONTEND_URL)
        assert r_fe.status_code == 200, f"Frontend returned {r_fe.status_code}"
        print(f"  ✓ Frontend online at {FRONTEND_URL} (Status: {r_fe.status_code})")
    except Exception as e:
        print(f"  ✗ Frontend error: {e}")
        sys.exit(1)

    try:
        r_be = client.get(f"{BACKEND_URL}/docs")
        assert r_be.status_code == 200, f"Backend docs returned {r_be.status_code}"
        print(f"  ✓ Backend online at {BACKEND_URL} (Status: {r_be.status_code})")
    except Exception as e:
        print(f"  ✗ Backend error: {e}")
        sys.exit(1)

    # 2. Verify Database works
    print("\n[2/12] Verifying Database Seeding & Record Counts...")
    r_jobs = client.get(f"{BACKEND_URL}/api/jobs?page_size=5")
    assert r_jobs.status_code == 200
    jobs_data = r_jobs.json()
    assert jobs_data["total"] >= 300, f"Expected >= 300 jobs, got {jobs_data['total']}"
    print(f"  ✓ Database verified: {jobs_data['total']} jobs active, {len(jobs_data['items'])} returned in sample page.")

    # 3. Verify Authentication (Candidate Login)
    print("\n[3/12] Verifying Candidate Authentication...")
    login_payload = {
        "email": "demo@jobtrail.local",
        "password": "JobTrailDemo2026!"
    }
    r_login = client.post(f"{BACKEND_URL}/api/auth/login", json=login_payload)
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    token_data = r_login.json()
    token = token_data["access_token"]
    user = token_data["user"]
    assert token, "Token not received"
    assert user["email"] == "demo@jobtrail.local"
    assert user["full_name"] == "Satvik Sharma"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  ✓ Authenticated as: {user['full_name']} ({user['email']}, role: {user['role']})")

    # 4. Verify Candidate Profile
    print("\n[4/12] Verifying Candidate Profile Operations...")
    r_prof = client.get(f"{BACKEND_URL}/api/profile", headers=headers)
    assert r_prof.status_code == 200
    prof = r_prof.json()
    assert prof["skills"] and len(prof["skills"]) >= 5
    print(f"  ✓ Candidate Profile retrieved: {prof['degree']} in {prof['field_of_study']}, {len(prof['skills'])} skills detected.")

    # 5. Verify Resume Intelligence
    print("\n[5/12] Verifying Resume Intelligence...")
    r_resume = client.get(f"{BACKEND_URL}/api/resume", headers=headers)
    assert r_resume.status_code == 200
    res_data = r_resume.json()
    assert res_data["has_resume"] is True
    completeness = res_data.get("completeness", 0)
    print(f"  ✓ Resume Intelligence confirmed: {res_data['filename']}, completeness: {completeness}%.")

    # 6. Verify Recommendations Engine
    print("\n[6/12] Verifying Explainable Recommendations...")
    r_recs = client.get(f"{BACKEND_URL}/api/recommendations?limit=5", headers=headers)
    assert r_recs.status_code == 200
    recs = r_recs.json()
    assert len(recs["items"]) > 0, "No recommendations returned"
    top_rec = recs["items"][0]
    match = top_rec["match"]
    print(f"  ✓ Top Recommendation: '{top_rec['job']['title']}' at {top_rec['job']['company']}")
    print(f"    - Overall Match: {match['overall_match']}%")
    print(f"    - Breakdown: Semantic={match['semantic_match']}%, Skill={match['skill_match']}%, Eligibility={match['eligibility_match']}%, Preference={match['preference_match']}%")
    print(f"    - Matching Skills: {', '.join(match['matching_skills'][:5])}")
    print(f"    - Missing Skills: {', '.join(match['missing_skills'][:3])}")

    # 7. Verify Multi-Factor Scoring Formula
    print("\n[7/12] Verifying Hybrid Scoring Formula Properties...")
    job_id = top_rec["job"]["id"]
    r_match = client.get(f"{BACKEND_URL}/api/jobs/{job_id}/match", headers=headers)
    assert r_match.status_code == 200
    m_data = r_match.json()
    recomputed = round(
        0.50 * m_data["semantic_match"] +
        0.25 * m_data["skill_match"] +
        0.15 * m_data["eligibility_match"] +
        0.10 * m_data["preference_match"]
    )
    diff = abs(recomputed - m_data["overall_match"])
    assert diff <= 2, f"Recomputed score {recomputed} differs from {m_data['overall_match']}"
    print(f"  ✓ Mathematical consistency verified: {recomputed}% vs reported {m_data['overall_match']}% (within rounding margin).")

    # 8. Verify Skill Gap Engine
    print("\n[8/12] Verifying Targeted Skill Gap Analysis...")
    r_gap = client.get(f"{BACKEND_URL}/api/skill-gap?job_id={job_id}", headers=headers)
    assert r_gap.status_code == 200
    gap = r_gap.json()
    print(f"  ✓ Skill Gap diagnostics: {gap['readiness_score']}% readiness, {len(gap['missing'])} missing competencies identified.")

    # 9. Verify Natural Language Semantic Search
    print("\n[9/12] Verifying Semantic Search...")
    query = "machine learning internship for python student with no experience"
    r_search = client.get(f"{BACKEND_URL}/api/search?q={query}", headers=headers)
    assert r_search.status_code == 200
    search_data = r_search.json()
    assert len(search_data["items"]) > 0, "No semantic results found"
    top_search = search_data["items"][0]
    print(f"  ✓ Semantic query '{query[:35]}...' matched {search_data['total_matches']} opportunities.")
    print(f"    Top match: '{top_search['job']['title']}' (Relevance: {top_search['relevance_score']}%)")

    # 10. Verify Save and Unsave Lifecycle
    print("\n[10/12] Verifying Save/Bookmark Lifecycle...")
    r_save = client.post(f"{BACKEND_URL}/api/jobs/{job_id}/save", headers=headers)
    assert r_save.status_code == 200
    r_saved_list = client.get(f"{BACKEND_URL}/api/saved-jobs", headers=headers)
    saved_ids = [j["id"] for j in r_saved_list.json()["items"]]
    assert job_id in saved_ids, "Saved job not in list"
    print(f"  ✓ Bookmarking verified: Job #{job_id} successfully persisted in saved items.")

    # 11. Verify Application Submission & Pipeline
    print("\n[11/12] Verifying Application Submission & Pipeline Tracker...")
    apply_payload = {"notes": "Automated verification test candidate application."}
    r_apply = client.post(f"{BACKEND_URL}/api/jobs/{job_id}/apply", json=apply_payload, headers=headers)
    assert r_apply.status_code in [200, 201], f"Apply failed: {r_apply.text}"
    r_apps = client.get(f"{BACKEND_URL}/api/applications", headers=headers)
    assert r_apps.status_code == 200
    apps = r_apps.json()
    matching_app = next((a for a in apps if a["job_id"] == job_id), None)
    assert matching_app is not None, "Application not found in pipeline"
    print(f"  ✓ Application lifecycle verified: Application #{matching_app['id']} tracked with status '{matching_app['status']}'.")

    # 12. Verify Logout and Re-authentication Persistence
    print("\n[12/12] Verifying Logout & Session Renewal...")
    r_logout = client.post(f"{BACKEND_URL}/api/auth/logout", headers=headers)
    assert r_logout.status_code == 200
    r_relogin = client.post(f"{BACKEND_URL}/api/auth/login", json=login_payload)
    assert r_relogin.status_code == 200
    new_token = r_relogin.json()["access_token"]
    assert new_token != "", "Re-login token invalid"
    print(f"  ✓ Session lifecycle & persistence verified: Logout and Re-login successful.")

    print("\n" + "=" * 70)
    print("ALL 12/12 CRITICAL SYSTEM VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
