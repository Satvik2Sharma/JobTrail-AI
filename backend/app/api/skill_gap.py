from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserSkill
from app.models.job import Job
from app.schemas.skill_gap import SkillGapResponse
from app.services.recommendation_service import recommendation_service
from app.ml.skill_gap import skill_gap_engine
from app.api.deps import get_current_user

router = APIRouter(tags=["Skill Gap Analysis"])

@router.get("/skill-gap", response_model=SkillGapResponse)
def get_skill_gap_analysis(
    job_id: Optional[int] = Query(None, description="Optional target job ID to analyze against"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive Skill Gap Analysis.
    Evaluates candidate skills against a specific job opportunity or against the top recommended roles.
    Returns acquired skills, missing competencies, priority rankings, and actionable guidance.
    """
    # 1. Fetch candidate skills
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    candidate_skills = [us.skill.name for us in user_skills if us.skill]

    if job_id:
        # Single job analysis
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        job_skills_data = [
            {"name": js.skill.name, "required": js.required, "importance": js.importance}
            for js in job.skills if js.skill
        ]

        return skill_gap_engine.analyze_job_skill_gap(
            candidate_skills=candidate_skills,
            job_skills=job_skills_data,
            job_id=job.id,
            job_title=f"{job.title} at {job.company}"
        )
    else:
        # Aggregate analysis across top recommendations
        rec_result = recommendation_service.get_recommendations(
            db=db,
            user_id=current_user.id,
            limit=5
        )

        top_jobs_skills = []
        for rec in rec_result.items:
            j = db.query(Job).filter(Job.id == rec.job.id).first()
            if j:
                s_data = [
                    {"name": js.skill.name, "required": js.required, "importance": js.importance}
                    for js in j.skills if js.skill
                ]
                top_jobs_skills.append(s_data)

        if not top_jobs_skills:
            # Fallback if no jobs recommended yet
            return SkillGapResponse(
                target_job_id=None,
                target_job_title="Top Opportunities",
                already_have=candidate_skills,
                missing=[],
                missing_details=[],
                career_insight="Add your skills and resume to generate targeted career gap insights.",
                readiness_score=100
            )

        return skill_gap_engine.analyze_aggregate_skill_gap(
            candidate_skills=candidate_skills,
            top_jobs_skills=top_jobs_skills,
            target_role_domain="your top recommended opportunities"
        )
