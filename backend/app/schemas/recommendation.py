from typing import List, Optional
from pydantic import BaseModel
from app.schemas.job import JobResponse

class MatchBreakdown(BaseModel):
    semantic_match: int # 0-100
    skill_match: int    # 0-100
    eligibility_match: int # 0-100
    preference_match: int  # 0-100

class ExplainableMatchResponse(BaseModel):
    job_id: int
    overall_match: int
    semantic_match: int
    skill_match: int
    eligibility_match: int
    preference_match: int
    matching_skills: List[str]
    missing_skills: List[str]
    explanation: List[str]

class JobRecommendationItem(BaseModel):
    job: JobResponse
    match: ExplainableMatchResponse

class RecommendationListResponse(BaseModel):
    total_matches: int
    items: List[JobRecommendationItem]

class CandidateRankingItem(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_email: str
    degree: Optional[str] = None
    experience_years: float = 0.0
    match: ExplainableMatchResponse
