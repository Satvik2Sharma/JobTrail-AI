from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="candidate") # "candidate" or "recruiter"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    posted_jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan", order_by="desc(Resume.created_at)")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    preferred_location = Column(String(255), nullable=True)
    remote_preference = Column(String(50), default="any") # "remote", "onsite", "hybrid", "any"
    education = Column(String(255), nullable=True) # e.g. "B.Tech", "M.S.", "Bachelor's"
    degree = Column(String(255), nullable=True) # e.g. "B.Tech Computer Science"
    field_of_study = Column(String(255), nullable=True) # e.g. "Computer Science"
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(String(50), nullable=True) # e.g. "3.85 / 4.0" or "8.9 / 10"
    experience_years = Column(Float, default=0.0)
    interests = Column(Text, nullable=True) # Comma-separated or JSON list of interests
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_extracted_data = Column(Text, nullable=True) # JSON of extracted sections (projects, certs, etc.)
    candidate_embedding_json = Column(Text, nullable=True) # JSON serialized candidate vector for instant recommendations
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="profile")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False) # Display name
    normalized_name = Column(String(100), unique=True, index=True, nullable=False) # Lowercase normalized
    category = Column(String(100), default="Technical")

    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")
    job_skills = relationship("JobSkill", back_populates="skill")

class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(String(50), default="intermediate") # "beginner", "intermediate", "advanced"
    source = Column(String(50), default="manual") # "resume", "manual", "inferred"

    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")
