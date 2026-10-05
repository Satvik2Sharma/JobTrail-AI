import pytest
import numpy as np
from app.ml.matching_engine import matching_engine
from app.ml.embeddings import embedding_service

def test_empty_profile_does_not_claim_100_percent():
    """
    Section 6: TEST UNKNOWN DATA
    A candidate profile with no skills, no education, no location,
    and no experience must NEVER produce 100% eligibility, 100% preference,
    or 100% overall match.
    """
    empty_cand_text = embedding_service.build_candidate_representation(
        degree=None,
        field=None,
        education=None,
        skills=[],
        experience_years=0.0,
        interests=None,
        resume_summary=None
    )
    empty_cand_vec = embedding_service.encode_candidate(empty_cand_text)

    # Job requiring Master's, 3+ years experience, and specific skills
    job_skills = [
        {"name": "Python", "required": True, "importance": 1.0},
        {"name": "Machine Learning", "required": True, "importance": 1.0},
        {"name": "Kubernetes", "required": True, "importance": 1.0}
    ]
    job_repr = embedding_service.build_job_representation(
        title="Senior AI Platform Engineer",
        category="Data Science & AI",
        skills=["Python", "Machine Learning", "Kubernetes"],
        description="Senior role building scalable AI infrastructure with Kubernetes and Python.",
        requirements="Master's degree and 3+ years experience.",
        experience_level="3+ years"
    )
    job_vec = embedding_service.encode_job(job_repr)

    match_result = matching_engine.match_candidate_to_job(
        candidate_embedding=empty_cand_vec,
        job_embedding=job_vec,
        candidate_skills=[],
        job_skills=job_skills,
        candidate_degree=None,
        candidate_field=None,
        candidate_education=None,
        candidate_exp_years=0.0,
        job_education_req="Master's in Computer Science",
        job_exp_level="3+ years",
        candidate_remote_pref=None,
        candidate_pref_location=None,
        candidate_interests=None,
        job_remote=False,
        job_location="New York, NY",
        job_category="Data Science & AI",
        job_id=99
    )

    # 1. Skill match must be 0% since candidate has no skills
    assert match_result["skill_match"] == 0
    assert len(match_result["matching_skills"]) == 0
    assert len(match_result["missing_skills"]) == 3

    # 2. Eligibility must not be 100%
    assert match_result["eligibility_match"] < 60
    assert match_result["eligibility_match"] > 0 # Neutral baseline, not 0

    # 3. Preference must not be 100% (neutral 50%)
    assert match_result["preference_match"] <= 55

    # 4. Overall match must be low, never near 100%
    assert match_result["overall_match"] < 40

    # 5. Explanations must transparently state missing criteria
    explanations = match_result["explanation"]
    assert any("not specified" in e.lower() for e in explanations)

def test_missing_preference_defaults_to_neutral():
    engine = matching_engine
    score, reasons = engine.compute_preference_match(
        candidate_remote_pref=None,
        candidate_pref_location=None,
        candidate_interests=None,
        job_remote=True,
        job_location="Remote",
        job_category="Software Engineering"
    )
    # Neutral baseline = 0.50 (50%)
    assert pytest.approx(score, 0.05) == 0.50
    assert any("not specified" in r.lower() for r in reasons)
