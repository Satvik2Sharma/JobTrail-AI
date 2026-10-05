import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserProfile, UserSkill, Skill
from app.models.resume import Resume
from app.models.job import Job
from app.models.application import Application
from app.api.deps import get_current_user
from app.resume.resume_service import resume_service
from app.ml.skill_extractor import skill_extractor
from app.ml.embeddings import embedding_service
from app.storage import get_storage_service

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete 15-step production resume pipeline:
    1. Authenticate user
    2. Validate uploaded file (filename, mime-type, magic bytes, size)
    3. Require application/pdf
    4. Enforce size limits
    5. Generate unique safe storage path
    6. Upload to private Supabase Storage (with local fallback)
    7. Extract text via PyMuPDF
    8. Detect extraction failure (empty, corrupted, scanned/image-only)
    9. Parse structured candidate information (CGPA, certs, projects, etc.)
    10. Normalize extracted skills with canonical taxonomy
    11. Update/create candidate profile without duplication
    12. Generate candidate embedding vector
    13. Save resume metadata in PostgreSQL (deactivating previous resumes)
    14. Save structured profile data
    15. Make recommendations available immediately
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename.")

    file_bytes = await file.read()

    # Step 2, 3, 4: File validation
    try:
        resume_service.validate_uploaded_file(file_bytes, file.filename, file.content_type)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    # Step 11 (Resume Replacement): Deactivate previous resumes for this candidate
    db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).update({"is_active": False})

    # Step 5 & 13: Create Resume database record
    resume_record = Resume(
        user_id=current_user.id,
        storage_path="", # placeholder
        original_filename=file.filename,
        mime_type="application/pdf",
        file_size=len(file_bytes),
        parsing_status="pending",
        parser_version="pymupdf_v1",
        is_active=True
    )
    db.add(resume_record)
    db.flush()

    safe_filename, storage_path = resume_service.generate_storage_path(
        user_id=current_user.id,
        resume_id=resume_record.id,
        original_filename=file.filename
    )
    resume_record.storage_path = storage_path

    # Step 6: Upload PDF to private Supabase Storage
    try:
        storage = get_storage_service()
        storage.upload_file(file_bytes, storage_path, content_type="application/pdf")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage upload failed: {str(e)}"
        )

    # Step 7 & 8: Extract text with PyMuPDF & detect scanned/empty/corrupted PDFs
    try:
        raw_text = resume_service.extract_text(file_bytes)
    except ValueError as e:
        resume_record.parsing_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        resume_record.parsing_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {str(e)}"
        )

    # Step 9: Parse structured candidate information without hallucination
    try:
        extracted = resume_service.parse_resume_intelligence(raw_text)
    except Exception as e:
        resume_record.parsing_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Information extraction failed: {str(e)}"
        )

    # Step 11: Update/create candidate UserProfile (never duplicate profile records)
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.resume_filename = safe_filename
    profile.resume_text = raw_text
    profile.resume_extracted_data = json.dumps(extracted)

    # Synchronize profile fields with active resume intelligence
    if extracted.get("phone"):
        profile.phone = extracted["phone"]
    if extracted.get("location"):
        profile.location = extracted["location"]
    if extracted.get("degree"):
        profile.degree = extracted["degree"]
    if extracted.get("education"):
        profile.education = extracted["education"]
    if extracted.get("field_of_study"):
        profile.field_of_study = extracted["field_of_study"]
    if extracted.get("graduation_year"):
        profile.graduation_year = extracted["graduation_year"]
    if extracted.get("cgpa"):
        profile.cgpa = extracted["cgpa"]
    if extracted.get("experience_years"):
        profile.experience_years = extracted["experience_years"]
    if extracted.get("interests"):
        profile.interests = ", ".join(extracted["interests"]) if isinstance(extracted["interests"], list) else str(extracted["interests"])

    # Step 10: Skill Normalization with canonical taxonomy
    detected_skills = extracted.get("detected_skills", [])
    for skill_name in detected_skills:
        norm_name = skill_extractor.normalize_skill(skill_name)
        skill = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
        if not skill:
            skill = Skill(
                name=norm_name,
                normalized_name=norm_name.lower(),
                category=skill_extractor.get_category(norm_name)
            )
            db.add(skill)
            db.flush()

        # Link detected skill to UserSkill
        existing_us = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == skill.id
        ).first()
        if not existing_us:
            new_us = UserSkill(
                user_id=current_user.id,
                skill_id=skill.id,
                proficiency="intermediate",
                source="resume"
            )
            db.add(new_us)

    # Step 12: Candidate Embedding Generation & persistence
    user_skills_list = [
        us.skill.name for us in db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all() if us.skill
    ]
    cand_text = embedding_service.build_candidate_representation(
        degree=profile.degree,
        field=profile.field_of_study,
        education=profile.education,
        skills=user_skills_list or detected_skills,
        experience_years=float(profile.experience_years or 0.0),
        interests=profile.interests,
        resume_summary=raw_text[:400]
    )
    cand_embedding = embedding_service.encode_candidate(cand_text)
    profile.candidate_embedding_json = json.dumps(cand_embedding.tolist())

    # Step 13: Finalize resume record metadata
    resume_record.parsing_status = "completed"
    resume_record.extracted_data = json.dumps(extracted)
    resume_record.raw_text = raw_text

    db.commit()
    db.refresh(resume_record)
    db.refresh(profile)

    return {
        "status": "completed",
        "message": "Resume successfully uploaded, parsed, and candidate intelligence extracted.",
        "resume_id": resume_record.id,
        "filename": safe_filename,
        "storage_path": storage_path,
        "file_size": len(file_bytes),
        "mime_type": "application/pdf",
        "parser_version": "pymupdf_v1",
        "intelligence": extracted,
        "skills_detected_count": len(detected_skills),
        "embedding_generated": True,
        "created_at": resume_record.created_at.isoformat() if resume_record.created_at else None
    }

@router.get("")
def get_resume_intelligence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve saved resume intelligence data, active resume, and upload history."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    active_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()

    all_resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    if not active_resume and (not profile or not profile.resume_filename):
        return {
            "has_resume": False,
            "message": "No resume uploaded yet.",
            "resumes": []
        }

    extracted = None
    if active_resume and active_resume.extracted_data:
        try:
            extracted = json.loads(active_resume.extracted_data)
        except Exception:
            extracted = None
    elif profile and profile.resume_extracted_data:
        try:
            extracted = json.loads(profile.resume_extracted_data)
        except Exception:
            extracted = None

    resume_history = [
        {
            "id": r.id,
            "filename": r.original_filename,
            "storage_path": r.storage_path,
            "file_size": r.file_size,
            "parsing_status": r.parsing_status,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in all_resumes
    ]

    filename = active_resume.original_filename if active_resume else (profile.resume_filename if profile else None)
    storage_path = active_resume.storage_path if active_resume else None

    return {
        "has_resume": True,
        "resume_id": active_resume.id if active_resume else None,
        "filename": filename,
        "storage_path": storage_path,
        "intelligence": extracted,
        "completeness": extracted.get("profile_completeness", 0) if extracted else 0,
        "resumes": resume_history
    }

@router.get("/{resume_id}")
def get_resume_by_id(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve specific resume metadata with strict ownership authorization.
    Users cannot access resumes belonging to another user.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # Strict authorization check
    if resume.user_id != current_user.id:
        # Check if current_user is recruiter for a job applied by this candidate
        is_recruiter_authorized = False
        if current_user.role == "recruiter":
            app = (
                db.query(Application)
                .join(Job, Application.job_id == Job.id)
                .filter(Job.recruiter_id == current_user.id, Application.user_id == resume.user_id)
                .first()
            )
            if app:
                is_recruiter_authorized = True

        if not is_recruiter_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to view this resume."
            )

    extracted = None
    if resume.extracted_data:
        try:
            extracted = json.loads(resume.extracted_data)
        except Exception:
            extracted = None

    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "original_filename": resume.original_filename,
        "storage_path": resume.storage_path,
        "file_size": resume.file_size,
        "mime_type": resume.mime_type,
        "parsing_status": resume.parsing_status,
        "is_active": resume.is_active,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "intelligence": extracted
    }

@router.get("/download/{storage_path:path}")
def download_resume_by_path(
    storage_path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download private resume document with strict ownership verification.
    Prevents unauthorized access across candidates.
    """
    resume = db.query(Resume).filter(Resume.storage_path == storage_path).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    # Ownership check
    if resume.user_id != current_user.id:
        is_recruiter_authorized = False
        if current_user.role == "recruiter":
            app = (
                db.query(Application)
                .join(Job, Application.job_id == Job.id)
                .filter(Job.recruiter_id == current_user.id, Application.user_id == resume.user_id)
                .first()
            )
            if app:
                is_recruiter_authorized = True

        if not is_recruiter_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You cannot download another user's private resume."
            )

    try:
        storage = get_storage_service()
        file_bytes = storage.download_file(storage_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume file missing from storage.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file from storage: {str(e)}")

    safe_filename = resume.original_filename or "resume.pdf"
    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"'
        }
    )
