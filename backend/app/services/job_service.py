from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from app.models.job import Job, JobSkill, JobEmbedding, SavedJob
from app.models.user import Skill
from app.models.application import Application
from app.schemas.job import JobCreate, JobResponse
from app.ml.embeddings import embedding_service
from app.ml.skill_extractor import skill_extractor
import json

class JobService:
    def get_job(self, db: Session, job_id: int, user_id: Optional[int] = None) -> Optional[JobResponse]:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None
        return self._format_job(db, job, user_id)

    def list_jobs(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        remote: Optional[bool] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        keyword: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[List[JobResponse], int]:
        query = db.query(Job)

        if category and category.lower() != "all":
            query = query.filter(Job.category == category)
        
        if remote is not None:
            query = query.filter(Job.remote == remote)

        if location and location.strip():
            query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

        if employment_type and employment_type.lower() != "all":
            query = query.filter(Job.employment_type.ilike(f"%{employment_type.strip()}%"))

        if experience_level and experience_level.lower() != "all":
            query = query.filter(Job.experience_level.ilike(f"%{experience_level.strip()}%"))

        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    Job.title.ilike(kw),
                    Job.company.ilike(kw),
                    Job.description.ilike(kw),
                    Job.category.ilike(kw)
                )
            )

        total = query.count()
        jobs = query.order_by(desc(Job.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        formatted = [self._format_job(db, j, user_id) for j in jobs]
        return formatted, total

    def save_job(self, db: Session, user_id: int, job_id: int) -> bool:
        existing = db.query(SavedJob).filter(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        ).first()
        if existing:
            return True # already saved
        saved = SavedJob(user_id=user_id, job_id=job_id)
        db.add(saved)
        db.commit()
        return True

    def unsave_job(self, db: Session, user_id: int, job_id: int) -> bool:
        saved = db.query(SavedJob).filter(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        ).first()
        if saved:
            db.delete(saved)
            db.commit()
            return True
        return False

    def get_saved_jobs(self, db: Session, user_id: int) -> List[JobResponse]:
        saved_records = db.query(SavedJob).filter(SavedJob.user_id == user_id).order_by(desc(SavedJob.created_at)).all()
        jobs = []
        for s in saved_records:
            job = db.query(Job).filter(Job.id == s.job_id).first()
            if job:
                jobs.append(self._format_job(db, job, user_id))
        return jobs

    def create_recruiter_job(self, db: Session, job_in: JobCreate, recruiter_id: int) -> JobResponse:
        job = Job(
            title=job_in.title,
            company=job_in.company,
            location=job_in.location,
            remote=job_in.remote,
            employment_type=job_in.employment_type,
            experience_level=job_in.experience_level,
            education_requirement=job_in.education_requirement,
            category=job_in.category,
            description=job_in.description,
            requirements=job_in.requirements,
            responsibilities=job_in.responsibilities,
            salary_min=job_in.salary_min,
            salary_max=job_in.salary_max,
            application_url=job_in.application_url,
            created_by=recruiter_id
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Link skills
        for skill_name in job_in.skills:
            norm_name = skill_extractor.normalize_skill(skill_name)
            skill = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
            if not skill:
                skill = Skill(
                    name=norm_name,
                    normalized_name=norm_name.lower(),
                    category=skill_extractor.get_category(norm_name)
                )
                db.add(skill)
                db.commit()
                db.refresh(skill)

            job_skill = JobSkill(job_id=job.id, skill_id=skill.id, required=True, importance=1.0)
            db.add(job_skill)

        # Generate and store embedding
        job_repr = embedding_service.build_job_representation(
            title=job.title,
            category=job.category,
            skills=job_in.skills,
            description=job.description,
            requirements=job.requirements,
            experience_level=job.experience_level
        )
        embedding_vec = embedding_service.encode_job(job_repr)
        emb_record = JobEmbedding(
            job_id=job.id,
            embedding_json=json.dumps(embedding_vec.tolist())
        )
        db.add(emb_record)
        db.commit()

        return self._format_job(db, job, recruiter_id)

    def _format_job(self, db: Session, job: Job, user_id: Optional[int] = None) -> JobResponse:
        # Load skills
        skill_names = [js.skill.name for js in job.skills if js.skill]
        
        is_saved = False
        has_applied = False
        app_status = None

        if user_id:
            saved = db.query(SavedJob).filter(
                SavedJob.user_id == user_id,
                SavedJob.job_id == job.id
            ).first()
            is_saved = saved is not None

            app = db.query(Application).filter(
                Application.user_id == user_id,
                Application.job_id == job.id
            ).first()
            if app:
                has_applied = True
                app_status = app.status

        return JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            remote=job.remote,
            employment_type=job.employment_type,
            experience_level=job.experience_level,
            education_requirement=job.education_requirement,
            category=job.category,
            description=job.description,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            application_url=job.application_url,
            skills=skill_names,
            is_saved=is_saved,
            has_applied=has_applied,
            application_status=app_status,
            created_at=job.created_at
        )

job_service = JobService()
