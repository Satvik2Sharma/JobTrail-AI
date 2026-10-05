from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.job import JobResponse, JobListResponse
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.job_service import job_service
from app.services.application_service import application_service
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter(tags=["Jobs"])

@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """List jobs with flexible search filters, pagination, and saved/applied indicators."""
    user_id = current_user.id if current_user else None
    items, total = job_service.list_jobs(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        remote=remote,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        keyword=keyword,
        user_id=user_id
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )

@router.get("/jobs/{id}", response_model=JobResponse)
def get_job(
    id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get single job details by ID."""
    user_id = current_user.id if current_user else None
    job = job_service.get_job(db, id, user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.post("/jobs/{id}/save")
def save_job(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a job opportunity to candidate's bookmarks."""
    job = job_service.get_job(db, id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    job_service.save_job(db, current_user.id, id)
    return {"message": "Job successfully saved.", "saved": True}

@router.delete("/jobs/{id}/save")
def unsave_job(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a job from saved bookmarks."""
    removed = job_service.unsave_job(db, current_user.id, id)
    return {"message": "Job removed from saved bookmarks.", "saved": False}

@router.get("/saved-jobs")
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all saved jobs for current candidate."""
    jobs = job_service.get_saved_jobs(db, current_user.id)
    return {"total": len(jobs), "items": jobs}

@router.post("/jobs/{id}/apply", response_model=ApplicationResponse)
def apply_to_job(
    id: int,
    req: Optional[ApplicationCreate] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit application for job and track in application pipeline."""
    job = job_service.get_job(db, id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    notes = req.notes if req else None
    app = application_service.apply_to_job(db, current_user.id, id, notes)
    return app
