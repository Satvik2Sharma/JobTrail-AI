import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile, UserSkill, Skill
from app.models.job import Job, JobSkill
from app.services.recommendation_service import recommendation_service
from app.core.security import get_password_hash

def test_recommendation_ranking_candidate_a_synthetic_fixture(db_session: Session):
    """
    Section 39 Test Fixture:
    Candidate A:
      Education: B.Tech Computer Science
      Skills: Python, Machine Learning, Pandas, NumPy, SQL, FastAPI, React, Git
      Experience: 0-1 years (0.5 years)
    
    Jobs in seeded DB:
      1. Machine Learning Intern (Strong match - Python, ML, Pandas, NumPy, SQL, Entry level, remote)
      2. Junior Backend Developer (Moderate match - Python, FastAPI, Docker, PostgreSQL, 1-2 years)
      3. Senior Cloud Infrastructure Architect (Weak match - Kubernetes, AWS, CI/CD, 3+ years)

    Verify that:
      ML Intern Score > Junior Backend Developer Score > Senior Cloud Architect Score.
    """
    candidate = db_session.query(User).filter(User.email == "test_candidate@jobtrail.local").first()
    assert candidate is not None

    recs = recommendation_service.get_recommendations(db_session, candidate.id, limit=10)
    assert recs.total_matches >= 3

    # Extract titles and match scores
    ranked_jobs = [(item.job.title, item.match.overall_match) for item in recs.items]
    titles = [item.job.title for item in recs.items]

    ml_intern_score = next(item.match.overall_match for item in recs.items if item.job.title == "Machine Learning Intern")
    backend_score = next(item.match.overall_match for item in recs.items if item.job.title == "Junior Backend Developer")
    cloud_score = next(item.match.overall_match for item in recs.items if item.job.title == "Senior Cloud Infrastructure Architect")

    # High match for ML Intern (skills & degree match)
    assert ml_intern_score >= 80, f"Expected ML Intern score >= 80, got {ml_intern_score}"
    # Moderate match for Backend Dev
    assert backend_score >= 50, f"Expected Backend score >= 50, got {backend_score}"
    # Weak match for Senior Cloud role
    assert cloud_score < backend_score, f"Cloud ({cloud_score}) should be lower than Backend ({backend_score})"
    assert ml_intern_score > backend_score, f"ML Intern ({ml_intern_score}) should outrank Backend ({backend_score})"

    # Check ranking position
    assert titles.index("Machine Learning Intern") < titles.index("Junior Backend Developer")
    assert titles.index("Junior Backend Developer") < titles.index("Senior Cloud Infrastructure Architect")

def test_multiple_candidates_ranking_differential(db_session: Session):
    """
    Test Candidate B (Frontend specialist) and Candidate C (DevOps specialist).
    Verify each candidate gets their respective domain job ranked highest.
    """
    # 1. Create Frontend Candidate B
    user_b = User(
        email="candidate_b@jobtrail.local",
        password_hash=get_password_hash("Pass123!"),
        full_name="Frontend Dev",
        role="candidate"
    )
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_b)

    prof_b = UserProfile(
        user_id=user_b.id,
        education="B.Tech",
        degree="B.Tech Computer Science",
        field_of_study="Computer Science",
        experience_years=1.0,
        interests="Frontend, Web Development, UI/UX"
    )
    db_session.add(prof_b)
    for s in ["React", "TypeScript"]:
        sk = db_session.query(Skill).filter(Skill.normalized_name == s.lower()).first()
        if sk:
            db_session.add(UserSkill(user_id=user_b.id, skill_id=sk.id, proficiency="advanced", source="manual"))
    db_session.commit()

    # 2. Create DevOps Candidate C
    user_c = User(
        email="candidate_c@jobtrail.local",
        password_hash=get_password_hash("Pass123!"),
        full_name="Cloud DevOps Eng",
        role="candidate"
    )
    db_session.add(user_c)
    db_session.commit()
    db_session.refresh(user_c)

    prof_c = UserProfile(
        user_id=user_c.id,
        education="B.Tech",
        degree="B.Tech Computer Science",
        field_of_study="Computer Science",
        experience_years=3.5,
        interests="Cloud, DevOps, Infrastructure, Kubernetes"
    )
    db_session.add(prof_c)
    for s in ["Kubernetes", "AWS", "CI/CD", "Linux"]:
        sk = db_session.query(Skill).filter(Skill.normalized_name == s.lower()).first()
        if sk:
            db_session.add(UserSkill(user_id=user_c.id, skill_id=sk.id, proficiency="advanced", source="manual"))
    db_session.commit()

    # Get Candidate C recommendations: Senior Cloud Architect should outrank ML Intern!
    recs_c = recommendation_service.get_recommendations(db_session, user_c.id)
    c_cloud_score = next(item.match.overall_match for item in recs_c.items if item.job.title == "Senior Cloud Infrastructure Architect")
    c_ml_score = next(item.match.overall_match for item in recs_c.items if item.job.title == "Machine Learning Intern")

    assert c_cloud_score > c_ml_score, f"Candidate C should prefer Cloud Architect ({c_cloud_score}) over ML Intern ({c_ml_score})"
