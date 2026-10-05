import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserProfile, UserSkill, Skill
from app.schemas.profile import ProfileUpdate, ProfileResponse, SkillItem, UserSkillAddRequest
from app.api.deps import get_current_user
from app.ml.skill_extractor import skill_extractor
from app.resume.resume_service import resume_service

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full profile, skills, and calculated profile completeness."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    skill_items = [
        SkillItem(
            id=us.id,
            name=us.skill.name,
            category=us.skill.category,
            proficiency=us.proficiency,
            source=us.source
        )
        for us in user_skills if us.skill
    ]

    extracted_dict = None
    if profile.resume_extracted_data:
        try:
            extracted_dict = json.loads(profile.resume_extracted_data)
        except Exception:
            extracted_dict = None

    completeness = resume_service.calculate_completeness(
        name=current_user.full_name,
        email=current_user.email,
        phone=profile.phone,
        degree=profile.degree,
        field=profile.field_of_study,
        skills=[s.name for s in skill_items],
        experience_years=float(profile.experience_years or 0.0),
        projects=extracted_dict.get("sections", {}).get("projects", []) if extracted_dict else []
    )

    return ProfileResponse(
        id=profile.id,
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role,
        phone=profile.phone,
        location=profile.location,
        preferred_location=profile.preferred_location,
        remote_preference=profile.remote_preference,
        education=profile.education,
        degree=profile.degree,
        field_of_study=profile.field_of_study,
        graduation_year=profile.graduation_year,
        experience_years=float(profile.experience_years or 0.0),
        interests=profile.interests,
        resume_filename=profile.resume_filename,
        profile_completeness=completeness,
        skills=skill_items,
        extracted_data=extracted_dict
    )

@router.put("", response_model=ProfileResponse)
def update_profile(
    req: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile attributes and optionally sync skills."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if req.phone is not None:
        profile.phone = req.phone
    if req.location is not None:
        profile.location = req.location
    if req.preferred_location is not None:
        profile.preferred_location = req.preferred_location
    if req.remote_preference is not None:
        profile.remote_preference = req.remote_preference
    if req.education is not None:
        profile.education = req.education
    if req.degree is not None:
        profile.degree = req.degree
    if req.field_of_study is not None:
        profile.field_of_study = req.field_of_study
    if req.graduation_year is not None:
        profile.graduation_year = req.graduation_year
    if req.experience_years is not None:
        profile.experience_years = req.experience_years
    if req.interests is not None:
        profile.interests = req.interests

    # Update skills if provided
    if req.skills is not None:
        # Delete existing user skills
        db.query(UserSkill).filter(UserSkill.user_id == current_user.id).delete()
        for sk_str in req.skills:
            norm_name = skill_extractor.normalize_skill(sk_str)
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

            user_skill = UserSkill(
                user_id=current_user.id,
                skill_id=skill.id,
                proficiency="intermediate",
                source="manual"
            )
            db.add(user_skill)

    db.commit()
    db.refresh(profile)

    return get_profile(current_user=current_user, db=db)

@router.post("/skills", response_model=SkillItem)
def add_user_skill(
    req: UserSkillAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a single skill to candidate profile."""
    norm_name = skill_extractor.normalize_skill(req.name)
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

    existing = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id
    ).first()

    if existing:
        existing.proficiency = req.proficiency or existing.proficiency
        existing.source = req.source or existing.source
        db.commit()
        return SkillItem(
            id=existing.id,
            name=skill.name,
            category=skill.category,
            proficiency=existing.proficiency,
            source=existing.source
        )

    user_skill = UserSkill(
        user_id=current_user.id,
        skill_id=skill.id,
        proficiency=req.proficiency or "intermediate",
        source=req.source or "manual"
    )
    db.add(user_skill)
    db.commit()
    db.refresh(user_skill)

    return SkillItem(
        id=user_skill.id,
        name=skill.name,
        category=skill.category,
        proficiency=user_skill.proficiency,
        source=user_skill.source
    )

@router.delete("/skills/{skill_name}")
def remove_user_skill(
    skill_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a skill from candidate profile."""
    norm_name = skill_extractor.normalize_skill(skill_name)
    skill = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found.")

    deleted = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id
    ).delete()
    db.commit()

    if not deleted:
        raise HTTPException(status_code=404, detail="Skill was not attached to your profile.")

    return {"message": f"Skill '{norm_name}' removed.", "status": "ok"}
