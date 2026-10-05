import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserProfile, Skill, UserSkill
from app.models.job import Job, JobSkill, JobEmbedding
from app.ml.embeddings import embedding_service
from app.ml.skill_extractor import skill_extractor

# Use an isolated test database
TEST_DB_URL = "sqlite:///./test_jobtrail.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    # Seed core test skills
    skills_to_seed = [
        ("Python", "Programming Languages", ["python", "py"]),
        ("Machine Learning", "Data Science & AI", ["machine learning", "ml"]),
        ("Deep Learning", "Data Science & AI", ["deep learning", "dl"]),
        ("Pandas", "Data Science & AI", ["pandas"]),
        ("NumPy", "Data Science & AI", ["numpy"]),
        ("SQL", "Databases", ["sql"]),
        ("FastAPI", "Backend Development", ["fastapi"]),
        ("React", "Frontend Development", ["react", "react.js"]),
        ("TypeScript", "Programming Languages", ["typescript", "ts"]),
        ("Docker", "Cloud & DevOps", ["docker"]),
        ("AWS", "Cloud & DevOps", ["aws", "amazon web services"]),
        ("Git", "Tools & Version Control", ["git"]),
        ("Linux", "Tools & Version Control", ["linux"]),
        ("Data Structures", "Computer Science Fundamentals", ["data structures", "dsa"]),
        ("Algorithms", "Computer Science Fundamentals", ["algorithms"]),
        ("CI/CD", "Cloud & DevOps", ["ci/cd", "ci cd"]),
        ("Kubernetes", "Cloud & DevOps", ["kubernetes", "k8s"]),
        ("PostgreSQL", "Databases", ["postgresql", "postgres"]),
    ]

    for name, cat, aliases in skills_to_seed:
        sk = db.query(Skill).filter(Skill.normalized_name == name.lower()).first()
        if not sk:
            sk = Skill(name=name, normalized_name=name.lower(), category=cat)
            db.add(sk)
    db.commit()

    # Seed test users
    candidate = db.query(User).filter(User.email == "test_candidate@jobtrail.local").first()
    if not candidate:
        candidate = User(
            email="test_candidate@jobtrail.local",
            password_hash=get_password_hash("TestPassword123!"),
            full_name="Alex Chen",
            role="candidate"
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        profile = UserProfile(
            user_id=candidate.id,
            phone="+1 (555) 234-5678",
            location="San Francisco, CA",
            preferred_location="San Francisco, CA",
            remote_preference="hybrid",
            education="B.Tech",
            degree="B.Tech Computer Science",
            field_of_study="Computer Science",
            graduation_year=2025,
            experience_years=0.5,
            interests="Machine Learning, Data Science, Backend Systems",
            resume_text="Alex Chen - Computer Science undergraduate passionate about ML."
        )
        db.add(profile)
        db.commit()

        # Add candidate skills: Python, Machine Learning, Pandas, NumPy, SQL, FastAPI, React, Git
        cand_skills = ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "FastAPI", "React", "Git"]
        for s_name in cand_skills:
            sk = db.query(Skill).filter(Skill.normalized_name == s_name.lower()).first()
            if sk:
                us = UserSkill(user_id=candidate.id, skill_id=sk.id, proficiency="intermediate", source="manual")
                db.add(us)
        db.commit()

    recruiter = db.query(User).filter(User.email == "test_recruiter@jobtrail.local").first()
    if not recruiter:
        recruiter = User(
            email="test_recruiter@jobtrail.local",
            password_hash=get_password_hash("RecruiterPass123!"),
            full_name="Sarah Jenkins",
            role="recruiter"
        )
        db.add(recruiter)
        db.commit()

    # Seed 3 distinct jobs for testing recommendation ranking:
    # 1. Strong Match: Machine Learning Intern (Requires Python, ML, Pandas, SQL)
    # 2. Moderate Match: Backend Developer (Requires Python, SQL, Docker, AWS)
    # 3. Weak Match: Senior DevOps Lead (Requires Kubernetes, AWS, CI/CD, 5+ years experience)
    job_strong = db.query(Job).filter(Job.title == "Machine Learning Intern").first()
    if not job_strong:
        job_strong = Job(
            title="Machine Learning Intern",
            company="NeuralPath Labs",
            location="San Francisco, CA",
            remote=True,
            employment_type="Internship",
            experience_level="0-1 years",
            education_requirement="B.Tech in Computer Science or related field",
            category="Data Science & AI",
            description="Seeking a Machine Learning Intern to assist in training transformer models and data preprocessing using Python, Pandas, and NumPy.",
            requirements="Pursuing degree in Computer Science. Strong Python and ML fundamentals.",
            responsibilities="Develop ML prototypes, analyze datasets, and evaluate model accuracy."
        )
        db.add(job_strong)
        db.flush()

        for s_name in ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"]:
            sk = db.query(Skill).filter(Skill.normalized_name == s_name.lower()).first()
            if sk:
                db.add(JobSkill(job_id=job_strong.id, skill_id=sk.id, required=True, importance=1.0))
        db.commit()

    job_mod = db.query(Job).filter(Job.title == "Junior Backend Developer").first()
    if not job_mod:
        job_mod = Job(
            title="Junior Backend Developer",
            company="CloudFlow Technologies",
            location="San Francisco, CA",
            remote=False,
            employment_type="Full-time",
            experience_level="1-2 years",
            education_requirement="Bachelor's in Computer Science",
            category="Backend Development",
            description="Junior Backend Engineer to build robust REST APIs using FastAPI, Docker, and PostgreSQL databases.",
            requirements="Knowledge of Python, relational databases, and containerization.",
            responsibilities="Maintain REST endpoints and optimize database queries."
        )
        db.add(job_mod)
        db.flush()

        for s_name in ["Python", "FastAPI", "PostgreSQL", "Docker"]:
            sk = db.query(Skill).filter(Skill.normalized_name == s_name.lower()).first()
            if sk:
                db.add(JobSkill(job_id=job_mod.id, skill_id=sk.id, required=True, importance=1.0))
        db.commit()

    job_weak = db.query(Job).filter(Job.title == "Senior Cloud Infrastructure Architect").first()
    if not job_weak:
        job_weak = Job(
            title="Senior Cloud Infrastructure Architect",
            company="Enterprise Cloud Corp",
            location="Austin, TX",
            remote=False,
            employment_type="Full-time",
            experience_level="3+ years",
            education_requirement="Master's in Computer Engineering",
            category="Cloud & DevOps",
            description="Lead multi-cloud enterprise deployments with Kubernetes, AWS, Terraform, and comprehensive CI/CD automation.",
            requirements="5+ years managing Kubernetes clusters and cloud architectures.",
            responsibilities="Architect distributed multi-region Kubernetes clusters."
        )
        db.add(job_weak)
        db.flush()

        for s_name in ["Kubernetes", "AWS", "CI/CD", "Linux"]:
            sk = db.query(Skill).filter(Skill.normalized_name == s_name.lower()).first()
            if sk:
                db.add(JobSkill(job_id=job_weak.id, skill_id=sk.id, required=True, importance=1.0))
        db.commit()

    db.close()

    yield

    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_jobtrail.db"):
        os.remove("./test_jobtrail.db")

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def candidate_token(db_session: Session) -> str:
    user = db_session.query(User).filter(User.email == "test_candidate@jobtrail.local").first()
    return create_access_token(subject=user.id)

@pytest.fixture
def candidate_headers(candidate_token: str) -> dict:
    return {"Authorization": f"Bearer {candidate_token}"}

@pytest.fixture
def recruiter_token(db_session: Session) -> str:
    user = db_session.query(User).filter(User.email == "test_recruiter@jobtrail.local").first()
    return create_access_token(subject=user.id)

@pytest.fixture
def recruiter_headers(recruiter_token: str) -> dict:
    return {"Authorization": f"Bearer {recruiter_token}"}
