import pytest
import numpy as np
from app.ml.matching_engine import ExplainableMatchingEngine, matching_engine
from app.ml.embeddings import embedding_service
from app.ml.skill_extractor import skill_extractor
from app.core.config import settings

def test_skill_extractor_normalization():
    assert skill_extractor.normalize_skill("python") == "Python"
    assert skill_extractor.normalize_skill("py") == "Python"
    assert skill_extractor.normalize_skill("js") == "JavaScript"
    assert skill_extractor.normalize_skill("ts") == "TypeScript"
    assert skill_extractor.normalize_skill("sklearn") == "Scikit-learn"
    assert skill_extractor.normalize_skill("postgres") == "PostgreSQL"
    assert skill_extractor.normalize_skill("docker") == "Docker"
    assert skill_extractor.normalize_skill("k8s") == "Kubernetes"
    assert skill_extractor.normalize_skill("fastapi") == "FastAPI"

def test_skill_extractor_from_text():
    sample_text = """
    We are looking for a software engineer skilled in Python, FastAPI, and Docker.
    Knowledge of PostgreSQL, Redis, and React is a big plus.
    Experience with Machine Learning and Git.
    """
    extracted = skill_extractor.extract_skills_from_text(sample_text)
    assert "Python" in extracted
    assert "FastAPI" in extracted
    assert "Docker" in extracted
    assert "PostgreSQL" in extracted
    assert "Redis" in extracted
    assert "React" in extracted
    assert "Machine Learning" in extracted
    assert "Git" in extracted

def test_skill_match_full_overlap():
    engine = ExplainableMatchingEngine()
    candidate_skills = ["Python", "Machine Learning", "Pandas", "NumPy"]
    job_skills = [
        {"name": "Python", "required": True, "importance": 1.0},
        {"name": "Machine Learning", "required": True, "importance": 1.0},
        {"name": "Pandas", "required": True, "importance": 1.0},
        {"name": "NumPy", "required": True, "importance": 1.0},
    ]
    score, matched, missing = engine.compute_skill_match(candidate_skills, job_skills)
    assert score == 1.0
    assert len(matched) == 4
    assert len(missing) == 0

def test_skill_match_partial_overlap():
    engine = ExplainableMatchingEngine()
    candidate_skills = ["Python", "SQL"]
    job_skills = [
        {"name": "Python", "required": True, "importance": 1.0},
        {"name": "SQL", "required": True, "importance": 1.0},
        {"name": "Docker", "required": True, "importance": 1.0},
        {"name": "AWS", "required": True, "importance": 1.0},
    ]
    score, matched, missing = engine.compute_skill_match(candidate_skills, job_skills)
    # 2 out of 4 equal-weight skills
    assert pytest.approx(score, 0.01) == 0.50
    assert "Python" in matched
    assert "SQL" in matched
    assert "Docker" in missing
    assert "AWS" in missing

def test_skill_match_zero_overlap():
    engine = ExplainableMatchingEngine()
    candidate_skills = ["Flutter", "Dart"]
    job_skills = [
        {"name": "Python", "required": True, "importance": 1.0},
        {"name": "FastAPI", "required": True, "importance": 1.0},
    ]
    score, matched, missing = engine.compute_skill_match(candidate_skills, job_skills)
    assert score == 0.0
    assert len(matched) == 0
    assert len(missing) == 2

def test_eligibility_match_btech_cs_entry_level():
    engine = ExplainableMatchingEngine()
    # Candidate: B.Tech Computer Science student, 0.5 yrs exp
    # Job: B.Tech in CS or related, 0-1 years exp
    score, reasons = engine.compute_eligibility_match(
        candidate_degree="B.Tech Computer Science",
        candidate_field="Computer Science",
        candidate_education="B.Tech",
        candidate_exp_years=0.5,
        job_education_req="B.Tech in Computer Science or related field",
        job_exp_level="0-1 years"
    )
    assert score == 1.0
    assert any("satisfy educational requirements" in r for r in reasons)
    assert any("matches internship/entry-level" in r for r in reasons)

def test_eligibility_match_experience_gap():
    engine = ExplainableMatchingEngine()
    # Candidate has 0.5 years experience, Job seeks senior with 3+ years
    score, reasons = engine.compute_eligibility_match(
        candidate_degree="B.Tech Computer Science",
        candidate_field="Computer Science",
        candidate_education="B.Tech",
        candidate_exp_years=0.5,
        job_education_req="B.Tech Computer Science",
        job_exp_level="3+ years"
    )
    # Education satisfies (1.0), experience falls short (0.30)
    # Expected: 0.6 * 1.0 + 0.4 * 0.30 = 0.72
    assert pytest.approx(score, 0.01) == 0.72
    assert any("mid/senior level" in r for r in reasons)

def test_preference_match_remote_alignment():
    engine = ExplainableMatchingEngine()
    # Remote candidate applying for remote job
    score, reasons = engine.compute_preference_match(
        candidate_remote_pref="remote",
        candidate_pref_location="San Francisco, CA",
        candidate_interests="Machine Learning",
        job_remote=True,
        job_location="Remote",
        job_category="Machine Learning"
    )
    assert score == 1.0
    assert any("Remote flexibility matches" in r for r in reasons)

def test_preference_match_mismatch():
    engine = ExplainableMatchingEngine()
    # Candidate strictly wants remote, job is strictly on-site in New York while candidate prefers SF
    score, reasons = engine.compute_preference_match(
        candidate_remote_pref="remote",
        candidate_pref_location="San Francisco, CA",
        candidate_interests="Machine Learning",
        job_remote=False,
        job_location="New York, NY",
        job_category="Sales"
    )
    # Remote mismatch = 0.30, location mismatch = 0.55, interest mismatch = 0.80 -> avg ~ 0.55
    assert score < 0.65
    assert any("contrasting with your remote preference" in r for r in reasons)

def test_cosine_similarity_properties():
    # Unit vectors
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v3 = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    sim_identical = embedding_service.calculate_similarity(v1, v2)
    assert pytest.approx(sim_identical, 0.001) == 1.0

    sim_orthogonal = embedding_service.calculate_similarity(v1, v3)
    assert pytest.approx(sim_orthogonal, 0.001) == 0.0

def test_hybrid_matching_score_formula():
    engine = ExplainableMatchingEngine()

    cand_skills = ["Python", "Machine Learning"]
    job_skills = [{"name": "Python", "required": True, "importance": 1.0}]

    v1 = np.random.randn(384).astype(np.float32)
    v1 /= np.linalg.norm(v1)

    result = engine.match_candidate_to_job(
        candidate_embedding=v1,
        job_embedding=v1,
        candidate_skills=cand_skills,
        job_skills=job_skills,
        candidate_degree="B.Tech Computer Science",
        candidate_field="Computer Science",
        candidate_education="B.Tech",
        candidate_exp_years=0.5,
        job_education_req="B.Tech Computer Science",
        job_exp_level="0-1 years",
        candidate_remote_pref="remote",
        candidate_pref_location="San Francisco",
        candidate_interests="Data Science",
        job_remote=True,
        job_location="San Francisco",
        job_category="Data Science",
        job_id=42
    )

    # All metrics should be in valid bounds [0, 100]
    assert 0 <= result["overall_match"] <= 100
    assert 0 <= result["semantic_match"] <= 100
    assert 0 <= result["skill_match"] <= 100
    assert 0 <= result["eligibility_match"] <= 100
    assert 0 <= result["preference_match"] <= 100

    # Skill match is 100% since Python is required and candidate has Python
    assert result["skill_match"] == 100
    assert "Python" in result["matching_skills"]
    assert len(result["missing_skills"]) == 0
    assert len(result["explanation"]) > 0
    assert result["job_id"] == 42
