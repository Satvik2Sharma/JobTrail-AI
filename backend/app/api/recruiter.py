from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.schemas.recommendation import CandidateRankingItem
from app.services.job_service import job_service
from app.services.recommendation_service import recommendation_service
from app.api.deps import get_current_recruiter

router = APIRouter(prefix="/recruiter", tags=["Recruiter Operations"])

@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_posting(
    req: JobCreate,
    current_recruiter: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Recruiter creates a new job posting with skill requirements and auto-generated embeddings."""
    job = job_service.create_recruiter_job(db, req, current_recruiter.id)
    return job

@router.get("/jobs", response_model=List[JobResponse])
def get_recruiter_posted_jobs(
    current_recruiter: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """List jobs created by this recruiter."""
    jobs = db.query(Job).filter(Job.created_by == current_recruiter.id).all()
    return [job_service._format_job(db, j, current_recruiter.id) for j in jobs]

@router.get("/jobs/{id}/candidates", response_model=List[CandidateRankingItem])
def rank_candidates_for_job(
    id: int,
    current_recruiter: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """
    Ranks all candidate profiles against the job posting using JobTrail-AI's Explainable ML Matching Engine.
    Provides detailed score breakdown and matching/missing skills for each applicant/candidate.
    """
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found.")

    rankings = recommendation_service.rank_candidates_for_job(db, id)
    return rankings
