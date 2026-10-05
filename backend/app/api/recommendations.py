from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationListResponse, ExplainableMatchResponse
from app.services.recommendation_service import recommendation_service
from app.api.deps import get_current_user

router = APIRouter(tags=["Recommendations"])

@router.get("/recommendations", response_model=RecommendationListResponse)
def get_recommendations(
    limit: int = Query(30, ge=1, le=100),
    min_match_score: int = Query(0, ge=0, le=100),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve personalized job recommendations ranked by JobTrail-AI's hybrid ML matching engine.
    Computes semantic similarity, skill overlap, eligibility, and preference alignment.
    """
    recommendations = recommendation_service.get_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit,
        min_match_score=min_match_score,
        category=category
    )
    return recommendations

@router.get("/jobs/{id}/match", response_model=ExplainableMatchResponse)
def get_job_match_breakdown(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detailed explainable match analysis between candidate and a specific job.
    Returns 4-dimensional score breakdown, matching skills, missing skills, and dynamic rationale.
    """
    match_resp = recommendation_service.get_job_match(db, current_user.id, id)
    if not match_resp:
        raise HTTPException(status_code=404, detail="Job not found.")
    return match_resp
