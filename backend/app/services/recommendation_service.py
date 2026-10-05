import json
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile, UserSkill, Skill
from app.models.job import Job, JobSkill, JobEmbedding
from app.schemas.recommendation import (
    ExplainableMatchResponse,
    JobRecommendationItem,
    RecommendationListResponse,
    CandidateRankingItem
)
from app.services.job_service import job_service
from app.ml.embeddings import embedding_service
from app.ml.matching_engine import matching_engine

class RecommendationService:
    """
    Orchestrates personalized job recommendations, explainable match evaluations,
    and recruiter candidate rankings using JobTrail-AI's hybrid ML engine.
    """

    def get_candidate_profile_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Fetch candidate profile, skills, and generate candidate embedding."""
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        user_skills = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == user_id)
            .all()
        )
        skills_list = [us.skill.name for us in user_skills if us.skill]

        degree = profile.degree if profile else None
        field = profile.field_of_study if profile else None
        education = profile.education if profile else None
        exp_years = float(profile.experience_years) if profile and profile.experience_years else 0.0
        remote_pref = profile.remote_preference if profile else "any"
        pref_location = profile.preferred_location if profile else None
        interests = profile.interests if profile else None
        resume_text = profile.resume_text if profile else None

        # Build candidate textual representation & vector
        cand_text = embedding_service.build_candidate_representation(
            degree=degree,
            field=field,
            education=education,
            skills=skills_list,
            experience_years=exp_years,
            interests=interests,
            resume_summary=resume_text[:400] if resume_text else None
        )
        cand_embedding = embedding_service.encode_candidate(cand_text)

        return {
            "user": user,
            "profile": profile,
            "skills": skills_list,
            "degree": degree,
            "field": field,
            "education": education,
            "exp_years": exp_years,
            "remote_pref": remote_pref,
            "pref_location": pref_location,
            "interests": interests,
            "embedding": cand_embedding,
        }

    def get_recommendations(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
        min_match_score: int = 0,
        category: Optional[str] = None
    ) -> RecommendationListResponse:
        cand_data = self.get_candidate_profile_data(db, user_id)
        cand_embedding = cand_data["embedding"]

        # Fetch jobs and their embeddings
        query = db.query(Job)
        if category and category.lower() != "all":
            query = query.filter(Job.category == category)

        jobs = query.all()
        if not jobs:
            return RecommendationListResponse(total_matches=0, items=[])

        # Pre-fetch embeddings
        job_ids = [j.id for j in jobs]
        embeddings_records = db.query(JobEmbedding).filter(JobEmbedding.job_id.in_(job_ids)).all()
        emb_map = {}
        for er in embeddings_records:
            try:
                emb_map[er.job_id] = np.array(json.loads(er.embedding_json), dtype=np.float32)
            except Exception:
                pass

        results: List[JobRecommendationItem] = []

        for job in jobs:
            # Prepare job skills
            job_skills_data = [
                {"name": js.skill.name, "required": js.required, "importance": js.importance}
                for js in job.skills if js.skill
            ]

            # Get job embedding or compute fallback
            job_emb = emb_map.get(job.id)
            if job_emb is None:
                job_repr = embedding_service.build_job_representation(
                    title=job.title,
                    category=job.category,
                    skills=[js.skill.name for js in job.skills if js.skill],
                    description=job.description,
                    requirements=job.requirements,
                    experience_level=job.experience_level
                )
                job_emb = embedding_service.encode_job(job_repr)

            # Match
            match_dict = matching_engine.match_candidate_to_job(
                candidate_embedding=cand_embedding,
                job_embedding=job_emb,
                candidate_skills=cand_data["skills"],
                job_skills=job_skills_data,
                candidate_degree=cand_data["degree"],
                candidate_field=cand_data["field"],
                candidate_education=cand_data["education"],
                candidate_exp_years=cand_data["exp_years"],
                job_education_req=job.education_requirement,
                job_exp_level=job.experience_level,
                candidate_remote_pref=cand_data["remote_pref"],
                candidate_pref_location=cand_data["pref_location"],
                candidate_interests=cand_data["interests"],
                job_remote=job.remote,
                job_location=job.location,
                job_category=job.category,
                job_id=job.id
            )

            if match_dict["overall_match"] >= min_match_score:
                formatted_job = job_service._format_job(db, job, user_id)
                match_response = ExplainableMatchResponse(**match_dict)
                results.append(JobRecommendationItem(job=formatted_job, match=match_response))

        # Sort descending by overall_match
        results.sort(key=lambda x: x.match.overall_match, reverse=True)
        top_items = results[:limit]

        return RecommendationListResponse(
            total_matches=len(results),
            items=top_items
        )

    def get_job_match(self, db: Session, user_id: int, job_id: int) -> Optional[ExplainableMatchResponse]:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        cand_data = self.get_candidate_profile_data(db, user_id)
        
        # Load job embedding
        emb_rec = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
        if emb_rec:
            job_emb = np.array(json.loads(emb_rec.embedding_json), dtype=np.float32)
        else:
            job_repr = embedding_service.build_job_representation(
                title=job.title,
                category=job.category,
                skills=[js.skill.name for js in job.skills if js.skill],
                description=job.description,
                requirements=job.requirements,
                experience_level=job.experience_level
            )
            job_emb = embedding_service.encode_job(job_repr)

        job_skills_data = [
            {"name": js.skill.name, "required": js.required, "importance": js.importance}
            for js in job.skills if js.skill
        ]

        match_dict = matching_engine.match_candidate_to_job(
            candidate_embedding=cand_data["embedding"],
            job_embedding=job_emb,
            candidate_skills=cand_data["skills"],
            job_skills=job_skills_data,
            candidate_degree=cand_data["degree"],
            candidate_field=cand_data["field"],
            candidate_education=cand_data["education"],
            candidate_exp_years=cand_data["exp_years"],
            job_education_req=job.education_requirement,
            job_exp_level=job.experience_level,
            candidate_remote_pref=cand_data["remote_pref"],
            candidate_pref_location=cand_data["pref_location"],
            candidate_interests=cand_data["interests"],
            job_remote=job.remote,
            job_location=job.location,
            job_category=job.category,
            job_id=job.id
        )

        return ExplainableMatchResponse(**match_dict)

    def rank_candidates_for_job(self, db: Session, job_id: int) -> List[CandidateRankingItem]:
        """Recruiter candidate ranking reusing the exact same explainable matching engine."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return []

        # Load job embedding
        emb_rec = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
        if emb_rec:
            job_emb = np.array(json.loads(emb_rec.embedding_json), dtype=np.float32)
        else:
            job_repr = embedding_service.build_job_representation(
                title=job.title,
                category=job.category,
                skills=[js.skill.name for js in job.skills if js.skill],
                description=job.description,
                requirements=job.requirements,
                experience_level=job.experience_level
            )
            job_emb = embedding_service.encode_job(job_repr)

        job_skills_data = [
            {"name": js.skill.name, "required": js.required, "importance": js.importance}
            for js in job.skills if js.skill
        ]

        # Fetch candidate users
        candidates = db.query(User).filter(User.role == "candidate").all()
        ranked: List[CandidateRankingItem] = []

        for cand in candidates:
            cand_data = self.get_candidate_profile_data(db, cand.id)
            match_dict = matching_engine.match_candidate_to_job(
                candidate_embedding=cand_data["embedding"],
                job_embedding=job_emb,
                candidate_skills=cand_data["skills"],
                job_skills=job_skills_data,
                candidate_degree=cand_data["degree"],
                candidate_field=cand_data["field"],
                candidate_education=cand_data["education"],
                candidate_exp_years=cand_data["exp_years"],
                job_education_req=job.education_requirement,
                job_exp_level=job.experience_level,
                candidate_remote_pref=cand_data["remote_pref"],
                candidate_pref_location=cand_data["pref_location"],
                candidate_interests=cand_data["interests"],
                job_remote=job.remote,
                job_location=job.location,
                job_category=job.category,
                job_id=job.id
            )

            ranked.append(
                CandidateRankingItem(
                    candidate_id=cand.id,
                    candidate_name=cand.full_name,
                    candidate_email=cand.email,
                    degree=cand_data["degree"],
                    experience_years=cand_data["exp_years"],
                    match=ExplainableMatchResponse(**match_dict)
                )
            )

        ranked.sort(key=lambda x: x.match.overall_match, reverse=True)
        return ranked

recommendation_service = RecommendationService()
