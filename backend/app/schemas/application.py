from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobResponse

class ApplicationCreate(BaseModel):
    status: Optional[str] = "applied" # "saved", "applied", "interview", "rejected", "selected"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int
    status: str
    notes: Optional[str] = None
    applied_at: datetime
    updated_at: Optional[datetime] = None
    job: JobResponse
