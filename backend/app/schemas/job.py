from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str
    remote: bool
    employment_type: str
    experience_level: str
    education_requirement: Optional[str] = None
    category: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_url: Optional[str] = None
    skills: List[str] = []
    is_saved: bool = False
    has_applied: bool = False
    application_status: Optional[str] = None
    created_at: Optional[datetime] = None

class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[JobResponse]

class JobCreate(BaseModel):
    title: str = Field(..., min_length=2)
    company: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    remote: bool = False
    employment_type: str = "Full-time"
    experience_level: str = "0-1 years"
    education_requirement: Optional[str] = None
    category: str = "Software Engineering"
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_url: Optional[str] = None
    skills: List[str] = []
