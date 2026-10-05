from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SkillItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None
    proficiency: str = "intermediate"
    source: str = "manual"

class UserSkillAddRequest(BaseModel):
    name: str
    proficiency: Optional[str] = "intermediate"
    source: Optional[str] = "manual"

class ProfileUpdate(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    preferred_location: Optional[str] = None
    remote_preference: Optional[str] = "any" # "remote", "onsite", "hybrid", "any"
    education: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_years: Optional[float] = 0.0
    interests: Optional[str] = None
    skills: Optional[List[str]] = None

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    full_name: str
    email: str
    role: str
    phone: Optional[str] = None
    location: Optional[str] = None
    preferred_location: Optional[str] = None
    remote_preference: Optional[str] = "any"
    education: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_years: float = 0.0
    interests: Optional[str] = None
    resume_filename: Optional[str] = None
    profile_completeness: int = 0 # Calculated percentage (0-100)
    skills: List[SkillItem] = []
    extracted_data: Optional[Dict[str, Any]] = None
