from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.job_service import job_service

class ApplicationService:
    def apply_to_job(self, db: Session, user_id: int, job_id: int, notes: Optional[str] = None) -> ApplicationResponse:
        existing = db.query(Application).filter(
            Application.user_id == user_id,
            Application.job_id == job_id
        ).first()

        if existing:
            if notes:
                existing.notes = notes
            db.commit()
            db.refresh(existing)
            job_resp = job_service.get_job(db, job_id, user_id)
            return ApplicationResponse(
                id=existing.id,
                user_id=existing.user_id,
                job_id=existing.job_id,
                status=existing.status,
                notes=existing.notes,
                applied_at=existing.applied_at,
                updated_at=existing.updated_at,
                job=job_resp
            )

        app = Application(user_id=user_id, job_id=job_id, status="applied", notes=notes)
        db.add(app)
        db.commit()
        db.refresh(app)

        job_resp = job_service.get_job(db, job_id, user_id)
        return ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            status=app.status,
            notes=app.notes,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            job=job_resp
        )

    def get_user_applications(self, db: Session, user_id: int) -> List[ApplicationResponse]:
        apps = db.query(Application).filter(Application.user_id == user_id).order_by(desc(Application.applied_at)).all()
        result = []
        for a in apps:
            job_resp = job_service.get_job(db, a.job_id, user_id)
            if job_resp:
                result.append(
                    ApplicationResponse(
                        id=a.id,
                        user_id=a.user_id,
                        job_id=a.job_id,
                        status=a.status,
                        notes=a.notes,
                        applied_at=a.applied_at,
                        updated_at=a.updated_at,
                        job=job_resp
                    )
                )
        return result

    def update_status(self, db: Session, application_id: int, status: str, user_id: int, notes: Optional[str] = None) -> Optional[ApplicationResponse]:
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return None
        
        # Enforce security: only the applicant or the job's creator recruiter may update
        if app.user_id != user_id:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if not job or job.created_by != user_id:
                raise PermissionError("You do not have permission to modify this application record.")

        app.status = status
        if notes is not None:
            app.notes = notes
        db.commit()
        db.refresh(app)
        job_resp = job_service.get_job(db, app.job_id, app.user_id)
        return ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            status=app.status,
            notes=app.notes,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            job=job_resp
        )

application_service = ApplicationService()
