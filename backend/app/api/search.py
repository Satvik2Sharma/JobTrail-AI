import json
import numpy as np
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.job import Job, JobEmbedding
from app.models.user import User
from app.schemas.job import JobResponse
from app.services.job_service import job_service
from app.ml.embeddings import embedding_service
from app.api.deps import get_current_user_optional

router = APIRouter(tags=["Semantic Search"])

@router.get("/search")
def semantic_search(
    q: str = Query(..., min_length=2, description="Natural language search query"),
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Natural Language Semantic Job Search.
    Encodes the query with SentenceTransformers, computes cosine similarity against all cached
    job vector embeddings, applies keyword boosting, and returns semantically ranked jobs.
    """
    user_id = current_user.id if current_user else None

    # 1. Encode user query
    query_vector = embedding_service.encode_text(q)

    # 2. Query jobs and embeddings
    jobs_query = db.query(Job)
    if category and category.lower() != "all":
        jobs_query = jobs_query.filter(Job.category == category)
    if remote is not None:
        jobs_query = jobs_query.filter(Job.remote == remote)

    jobs = jobs_query.all()
    if not jobs:
        return {"query": q, "total_matches": 0, "items": []}

    job_ids = [j.id for j in jobs]
    emb_records = db.query(JobEmbedding).filter(JobEmbedding.job_id.in_(job_ids)).all()
    emb_map = {}
    for er in emb_records:
        try:
            emb_map[er.job_id] = np.array(json.loads(er.embedding_json), dtype=np.float32)
        except Exception:
            pass

    q_tokens = [tok.lower() for tok in q.split() if len(tok) > 2]

    scored_jobs = []
    for job in jobs:
        job_vec = emb_map.get(job.id)
        if job_vec is None:
            job_repr = embedding_service.build_job_representation(
                title=job.title,
                category=job.category,
                skills=[js.skill.name for js in job.skills if js.skill],
                description=job.description,
                requirements=job.requirements,
                experience_level=job.experience_level
            )
            job_vec = embedding_service.encode_job(job_repr)

        # Cosine similarity
        cos_sim = embedding_service.calculate_similarity(query_vector, job_vec)

        # Keyword boost (bonus up to +0.15 if title or company directly contains query words)
        text_corpus = f"{job.title} {job.company} {job.category} {' '.join([js.skill.name for js in job.skills if js.skill])}".lower()
        matches_count = sum(1 for tok in q_tokens if tok in text_corpus)
        kw_boost = min(0.15, matches_count * 0.04)

        combined_score = cos_sim + kw_boost
        score_percent = int(round(min(1.0, max(0.0, (combined_score - 0.15) / 0.75)) * 100))

        formatted_job = job_service._format_job(db, job, user_id)
        scored_jobs.append({
            "job": formatted_job,
            "relevance_score": score_percent,
            "raw_similarity": float(cos_sim)
        })

    # Sort descending by relevance score
    scored_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_results = scored_jobs[:limit]

    return {
        "query": q,
        "total_matches": len(scored_jobs),
        "items": top_results
    }
