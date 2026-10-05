import os
import json
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal, Base
from app.models.user import User, UserProfile, Skill, UserSkill
from app.models.job import Job, JobSkill, JobEmbedding
from app.core.security import get_password_hash
from app.ml.embeddings import embedding_service
from app.ml.skill_extractor import skill_extractor

def seed_database():
    print("=" * 60)
    print("JobTrail-AI Database Seeding & Vector Embedding Pipeline")
    print("=" * 60)

    # 1. Create tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 2. Seed Skills Taxonomy from data/skills.json
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        skills_path = base_dir / "data" / "skills.json"
        
        if skills_path.exists():
            with open(skills_path, "r", encoding="utf-8") as f:
                skills_data = json.load(f)
            
            existing_skills = {s.normalized_name for s in db.query(Skill).all()}
            new_skills_count = 0
            for s in skills_data:
                norm = s["name"].strip().lower()
                if norm not in existing_skills:
                    skill_obj = Skill(
                        name=s["name"].strip(),
                        normalized_name=norm,
                        category=s.get("category", "Technical")
                    )
                    db.add(skill_obj)
                    existing_skills.add(norm)
                    new_skills_count += 1
            db.commit()
            print(f"[1/4] Skill taxonomy synced. Added {new_skills_count} new skills.")
        else:
            print(f"[1/4] Warning: {skills_path} not found.")

        # 3. Seed Demo Candidate & Recruiter Accounts
        demo_candidate = db.query(User).filter(User.email == "demo@jobtrail.local").first()
        if not demo_candidate:
            demo_candidate = User(
                email="demo@jobtrail.local",
                password_hash=get_password_hash("JobTrailDemo2026!"),
                full_name="Alex Chen",
                role="candidate"
            )
            db.add(demo_candidate)
            db.commit()
            db.refresh(demo_candidate)

            # Profile
            profile = UserProfile(
                user_id=demo_candidate.id,
                phone="+1 (555) 234-5678",
                location="San Francisco, CA",
                preferred_location="San Francisco, CA",
                remote_preference="hybrid",
                education="B.Tech",
                degree="B.Tech Computer Science",
                field_of_study="Computer Science",
                graduation_year=2025,
                experience_years=0.5,
                interests="Machine Learning, Data Science, Backend Systems, Python",
                resume_filename=None,
                resume_text="Alex Chen - Computer Science Undergraduate. Passionate about machine learning, distributed backend systems, and data pipelines. Built computer vision and recommendation engine projects."
            )
            db.add(profile)
            db.commit()

            # Attach core candidate skills
            initial_candidate_skills = [
                ("Python", "advanced"),
                ("Machine Learning", "intermediate"),
                ("Pandas", "intermediate"),
                ("NumPy", "intermediate"),
                ("SQL", "intermediate"),
                ("FastAPI", "intermediate"),
                ("React", "beginner"),
                ("Git", "intermediate"),
                ("Data Structures", "intermediate"),
                ("Algorithms", "intermediate")
            ]
            for s_name, prof in initial_candidate_skills:
                norm_name = skill_extractor.normalize_skill(s_name)
                sk = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
                if not sk:
                    sk = Skill(name=norm_name, normalized_name=norm_name.lower(), category="Technical")
                    db.add(sk)
                    db.commit()
                    db.refresh(sk)
                
                us = UserSkill(user_id=demo_candidate.id, skill_id=sk.id, proficiency=prof, source="manual")
                db.add(us)
            db.commit()
            print("[2/4] Seeded Demo Candidate: demo@jobtrail.local / JobTrailDemo2026!")
        else:
            print("[2/4] Demo Candidate already exists (idempotent skip).")

        demo_recruiter = db.query(User).filter(User.email == "recruiter@jobtrail.local").first()
        if not demo_recruiter:
            demo_recruiter = User(
                email="recruiter@jobtrail.local",
                password_hash=get_password_hash("RecruiterDemo2026!"),
                full_name="Sarah Jenkins (TechNova Talent)",
                role="recruiter"
            )
            db.add(demo_recruiter)
            db.commit()
            print("[2/4] Seeded Demo Recruiter: recruiter@jobtrail.local / RecruiterDemo2026!")

        # 4. Load & Seed Jobs Dataset from data/jobs.json
        jobs_path = base_dir / "data" / "jobs.json"
        if not jobs_path.exists():
            print(f"Error: {jobs_path} does not exist.")
            return

        with open(jobs_path, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)

        existing_titles_companies = {
            (j.title.strip().lower(), j.company.strip().lower()): j.id
            for j in db.query(Job).all()
        }

        print(f"[3/4] Processing {len(jobs_data)} job records from data/jobs.json...")
        new_jobs = []
        jobs_to_embed = []

        for record in jobs_data:
            key = (record["title"].strip().lower(), record["company"].strip().lower())
            if key in existing_titles_companies:
                job_id = existing_titles_companies[key]
                # Check if embedding already exists
                has_emb = db.query(JobEmbedding).filter(JobEmbedding.job_id == job_id).first()
                if not has_emb:
                    job_obj = db.query(Job).filter(Job.id == job_id).first()
                    if job_obj:
                        jobs_to_embed.append(job_obj)
                continue

            job = Job(
                title=record["title"],
                company=record["company"],
                location=record["location"],
                remote=record.get("remote", False),
                employment_type=record.get("employment_type", "Full-time"),
                experience_level=record.get("experience_level", "0-1 years"),
                education_requirement=record.get("education_requirement"),
                category=record.get("category", "Software Engineering"),
                description=record["description"],
                requirements=record.get("requirements"),
                responsibilities=record.get("responsibilities"),
                salary_min=record.get("salary_min"),
                salary_max=record.get("salary_max"),
                application_url=record.get("application_url"),
                created_by=None
            )
            db.add(job)
            db.flush() # get job.id

            # Add Job Skills
            for sk_name in record.get("skills", []):
                norm_name = skill_extractor.normalize_skill(sk_name)
                sk = db.query(Skill).filter(Skill.normalized_name == norm_name.lower()).first()
                if not sk:
                    sk = Skill(name=norm_name, normalized_name=norm_name.lower(), category=skill_extractor.get_category(norm_name))
                    db.add(sk)
                    db.flush()
                
                js = JobSkill(job_id=job.id, skill_id=sk.id, required=True, importance=1.0)
                db.add(js)

            new_jobs.append(job)
            jobs_to_embed.append(job)

        db.commit()
        print(f"[3/4] Inserted {len(new_jobs)} new job records into database.")

        # 5. Generate and Persist Sentence Transformer Embeddings
        print(f"[4/4] Computing embeddings for {len(jobs_to_embed)} jobs using {embedding_service.model_name}...")
        
        batch_size = 32
        embedded_count = 0

        for i in range(0, len(jobs_to_embed), batch_size):
            batch = jobs_to_embed[i:i + batch_size]
            texts = []
            for j in batch:
                skills_list = [js.skill.name for js in j.skills if js.skill]
                repr_text = embedding_service.build_job_representation(
                    title=j.title,
                    category=j.category,
                    skills=skills_list,
                    description=j.description,
                    requirements=j.requirements,
                    experience_level=j.experience_level
                )
                texts.append(repr_text)

            vectors = embedding_service.encode_batch(texts)

            for j, vec in zip(batch, vectors):
                emb_rec = JobEmbedding(
                    job_id=j.id,
                    embedding_json=json.dumps(vec.tolist())
                )
                db.add(emb_rec)
                embedded_count += 1

            db.commit()
            print(f"  -> Generated embeddings: {embedded_count}/{len(jobs_to_embed)} ({embedded_count*100//len(jobs_to_embed)}%)")

        print("=" * 60)
        print("Database seeding completed successfully!")
        total_jobs_in_db = db.query(Job).count()
        total_embeddings = db.query(JobEmbedding).count()
        print(f"Total Jobs in DB: {total_jobs_in_db}")
        print(f"Total Embeddings cached: {total_embeddings}")
        print("Demo Credentials:")
        print("  Candidate: demo@jobtrail.local / JobTrailDemo2026!")
        print("  Recruiter: recruiter@jobtrail.local / RecruiterDemo2026!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
