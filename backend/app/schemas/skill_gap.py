from typing import List, Optional
from pydantic import BaseModel

class MissingSkillDetail(BaseModel):
    skill: str
    frequency_in_target_roles: int = 1
    priority: str = "High" # "High", "Medium", "Low"
    category: Optional[str] = "Technical"

class SkillGapResponse(BaseModel):
    target_job_id: Optional[int] = None
    target_job_title: Optional[str] = None
    already_have: List[str]
    missing: List[str]
    missing_details: List[MissingSkillDetail] = []
    career_insight: str
    readiness_score: int # percentage
