import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserProfile, UserSkill, Skill
from app.api.deps import get_current_user
from app.resume.resume_service import resume_service
from app.ml.skill_extractor import skill_extractor

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse PDF resume using PyMuPDF.
    Extracts text, candidate details, normalized skills, and updates profile.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file (.pdf)."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        # 1. Save PDF file safely
        safe_filename, target_path = resume_service.save_uploaded_file(file_bytes, file.filename)

        # 2. Extract text with PyMuPDF
        raw_text = resume_service.extract_text_from_file(target_path)

        # 3. Resume Intelligence Extraction
        extracted = resume_service.parse_resume_intelligence(raw_text)

        # 4. Update UserProfile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)

        profile.resume_filename = safe_filename
        profile.resume_text = raw_text
        profile.resume_extracted_data = json.dumps(extracted)

        # Auto-fill profile fields if not already populated
        if extracted.get("phone") and not profile.phone:
            profile.phone = extracted["phone"]
        if extracted.get("degree") and not profile.degree:
            profile.degree = extracted["degree"]
        if extracted.get("education") and not profile.education:
            profile.education = extracted["education"]
        if extracted.get("field_of_study") and not profile.field_of_study:
            profile.field_of_study = extracted["field_of_study"]
        if extracted.get("graduation_year") and not profile.graduation_year:
            profile.graduation_year = extracted["graduation_year"]
        if extracted.get("experience_years") and not profile.experience_years:
            profile.experience_years = extracted["experience_years"]

        # Link detected skills to UserSkill with source="resume"
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
                db.commit()
                db.refresh(skill)

            # Avoid duplicate
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

        db.commit()
        db.refresh(profile)

        return {
            "status": "completed",
            "message": "Resume successfully parsed and intelligence extracted.",
            "filename": safe_filename,
            "intelligence": extracted,
            "skills_detected_count": len(detected_skills)
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )

@router.get("")
def get_resume_intelligence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve saved resume intelligence data and text statistics."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.resume_filename:
        return {
            "has_resume": False,
            "message": "No resume uploaded yet."
        }

    extracted = None
    if profile.resume_extracted_data:
        try:
            extracted = json.loads(profile.resume_extracted_data)
        except Exception:
            extracted = None

    return {
        "has_resume": True,
        "filename": profile.resume_filename,
        "intelligence": extracted,
        "completeness": profile.resume_extracted_data and extracted.get("profile_completeness", 0) or 0
    }
