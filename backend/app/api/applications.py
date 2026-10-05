from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import ApplicationResponse, ApplicationUpdate
from app.services.application_service import application_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["Application Tracking"])

@router.get("", response_model=List[ApplicationResponse])
def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all submitted applications for the current candidate."""
    return application_service.get_user_applications(db, current_user.id)

@router.put("/{id}", response_model=ApplicationResponse)
def update_application_status(
    id: int,
    req: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application progression status (applied, interview, rejected, selected)."""
    try:
        updated = application_service.update_status(db, id, req.status, current_user.id, req.notes)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))

    if not updated:
        raise HTTPException(status_code=404, detail="Application record not found.")
    return updated
