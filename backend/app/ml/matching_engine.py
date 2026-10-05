import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from app.core.config import settings
from app.ml.embeddings import embedding_service
from app.ml.skill_extractor import skill_extractor

class ExplainableMatchingEngine:
    """
    Explainable Career Matching Engine for JobTrail-AI.
    Combines:
      - Semantic vector similarity (Sentence-Transformers MiniLM)
      - Explicit weighted skill matching
      - Candidate eligibility verification (education, degree, experience)
      - Preference compatibility (remote, location, employment type)
    Produces deterministic, fully explainable match breakdowns and evidence-based justifications.
    """

    def __init__(self):
        self.semantic_weight = settings.SEMANTIC_WEIGHT
        self.skill_weight = settings.SKILL_WEIGHT
        self.eligibility_weight = settings.ELIGIBILITY_WEIGHT
        self.preference_weight = settings.PREFERENCE_WEIGHT

    def compute_skill_match(
        self,
        candidate_skills: List[str],
        job_skills: List[Dict[str, Any]] # [{"name": str, "required": bool, "importance": float}]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates skill match percentage, matched skills, and missing skills.
        Weights required skills and importance.
        Returns: (score_0_to_1, matched_list, missing_list)
        """
        if not job_skills:
            return 1.0, [], []

        # Normalize candidate skills
        cand_norm_set: Set[str] = {
            skill_extractor.normalize_skill(s).lower() for s in candidate_skills
        }

        total_weight = 0.0
        earned_weight = 0.0
        matched_skills: List[str] = []
        missing_skills: List[str] = []

        for item in job_skills:
            skill_name = item.get("name", "")
            norm_name = skill_extractor.normalize_skill(skill_name)
            is_required = item.get("required", True)
            importance = float(item.get("importance", 1.0))
            
            weight = importance * (1.5 if is_required else 1.0)
            total_weight += weight

            if norm_name.lower() in cand_norm_set:
                earned_weight += weight
                matched_skills.append(norm_name)
            else:
                missing_skills.append(norm_name)

        if total_weight == 0:
            score = 1.0
        else:
            score = earned_weight / total_weight

        return min(1.0, max(0.0, score)), matched_skills, missing_skills

    def compute_eligibility_match(
        self,
        candidate_degree: Optional[str],
        candidate_field: Optional[str],
        candidate_education: Optional[str],
        candidate_exp_years: float,
        job_education_req: Optional[str],
        job_exp_level: Optional[str]
    ) -> Tuple[float, List[str]]:
        """
        Evaluates educational background and experience requirements.
        Unknown or unspecified criteria explicitly receive a transparent neutral baseline (0.50).
        Returns (score_0_to_1, list_of_eligibility_reasons).
        """
        reasons: List[str] = []
        edu_score = 0.50 # Neutral baseline if unspecified
        exp_score = 0.50 # Neutral baseline if unspecified

        # 1. Education Evaluation
        cand_text = f"{candidate_degree or ''} {candidate_field or ''} {candidate_education or ''}".lower().strip()
        if job_education_req:
            job_req_clean = job_education_req.lower()

            # Degree level checks
            has_btech = any(k in cand_text for k in ["b.tech", "btech", "b.e", "be", "bachelor", "bs", "b.s", "undergraduate"])
            has_masters = any(k in cand_text for k in ["master", "m.tech", "mtech", "ms", "m.s", "mca"])
            
            req_bachelors = any(k in job_req_clean for k in ["b.tech", "b.e", "bachelor", "bs", "undergraduate"])
            req_masters = any(k in job_req_clean for k in ["master", "m.tech", "ms", "phd"])

            # Field checks
            field_match = False
            cs_fields = ["computer science", "cs", "cse", "information technology", "it", "software", "stem", "ai", "data science"]
            for f in cs_fields:
                if f in cand_text and (f in job_req_clean or "related" in job_req_clean or "stem" in job_req_clean):
                    field_match = True
                    break

            if not cand_text:
                edu_score = 0.50
                reasons.append("Education background not specified in candidate profile.")
            elif req_masters and has_masters:
                edu_score = 1.0
                reasons.append("Advanced degree satisfies the higher education requirement.")
            elif req_masters and not has_masters:
                edu_score = 0.40
                reasons.append("Role prefers a Master's degree.")
            elif req_bachelors and (has_btech or has_masters):
                if field_match:
                    edu_score = 1.0
                    reasons.append("Your degree and field of study fully satisfy educational requirements.")
                else:
                    edu_score = 0.85
                    reasons.append("Your degree satisfies the bachelor's requirement.")
            else:
                edu_score = 0.70
                reasons.append("Education appears broadly compatible with entry requirements.")
        else:
            if cand_text:
                edu_score = 0.90
                reasons.append("No strict degree gate specified for this role.")
            else:
                edu_score = 0.50
                reasons.append("Education background not specified.")

        # 2. Experience Evaluation
        if job_exp_level:
            exp_clean = job_exp_level.lower()
            if "intern" in exp_clean or "0-1" in exp_clean or "entry" in exp_clean:
                if candidate_exp_years >= 0:
                    exp_score = 1.0
                    reasons.append("Experience level matches internship/entry-level criteria.")
            elif "1-2" in exp_clean:
                if candidate_exp_years >= 1.0:
                    exp_score = 1.0
                    reasons.append("Your experience meets the 1-2 years threshold.")
                elif candidate_exp_years >= 0.5:
                    exp_score = 0.85
                    reasons.append("Close experience level with relevant project background.")
                else:
                    exp_score = 0.50
                    reasons.append("Role seeks 1-2 years experience; strong projects recommended.")
            elif "3+" in exp_clean or "senior" in exp_clean:
                if candidate_exp_years >= 3.0:
                    exp_score = 1.0
                else:
                    exp_score = 0.30
                    reasons.append("Role requires mid/senior level experience.")
            else:
                exp_score = 0.60
        else:
            exp_score = 0.70 if candidate_exp_years > 0 else 0.50

        eligibility_score = 0.6 * edu_score + 0.4 * exp_score
        return min(1.0, max(0.0, eligibility_score)), reasons

    def compute_preference_match(
        self,
        candidate_remote_pref: Optional[str],
        candidate_pref_location: Optional[str],
        candidate_interests: Optional[str],
        job_remote: bool,
        job_location: str,
        job_category: str
    ) -> Tuple[float, List[str]]:
        """
        Evaluates candidate workplace preferences against job attributes.
        Unspecified criteria explicitly receive a transparent neutral baseline (0.50).
        Returns (score_0_to_1, list_of_preference_reasons).
        """
        reasons: List[str] = []
        score_components = []

        # 1. Remote Preference
        cand_pref = (candidate_remote_pref or "").lower().strip()
        if cand_pref in ["remote", "only remote"]:
            if job_remote:
                score_components.append(1.0)
                reasons.append("Remote flexibility matches your remote work preference.")
            else:
                score_components.append(0.30)
                reasons.append("This role is on-site, contrasting with your remote preference.")
        elif cand_pref in ["onsite", "in-office"]:
            if not job_remote:
                score_components.append(1.0)
                reasons.append("On-site location aligns with your in-office preference.")
            else:
                score_components.append(0.70)
        elif cand_pref == "hybrid":
            score_components.append(0.90 if job_remote else 0.80)
            reasons.append("Flexible location accommodates your hybrid/open preference.")
        elif cand_pref == "any":
            score_components.append(0.80)
            reasons.append("Flexible with any work arrangement.")
        else:
            score_components.append(0.50) # Neutral baseline for unknown preference
            reasons.append("Workplace mode preference not specified.")

        # 2. Location Preference
        if candidate_pref_location and candidate_pref_location.strip():
            pref_loc = candidate_pref_location.lower().strip()
            job_loc = job_location.lower().strip()

            if job_remote or "remote" in job_loc:
                score_components.append(1.0)
            elif pref_loc in job_loc or job_loc in pref_loc:
                score_components.append(1.0)
                reasons.append(f"Located in your preferred area ({candidate_pref_location}).")
            else:
                score_components.append(0.40)
        else:
            score_components.append(0.50) # Neutral baseline for unknown location preference

        # 3. Domain / Category interest
        if candidate_interests and candidate_interests.strip():
            cand_int = candidate_interests.lower()
            if job_category.lower() in cand_int:
                score_components.append(1.0)
                reasons.append(f"Directly corresponds with your career interest in {job_category}.")
            else:
                score_components.append(0.50)
        else:
            score_components.append(0.50) # Neutral baseline for unknown interests

        pref_score = sum(score_components) / len(score_components)
        return min(1.0, max(0.0, pref_score)), reasons

    def match_candidate_to_job(
        self,
        candidate_embedding: np.ndarray,
        job_embedding: np.ndarray,
        candidate_skills: List[str],
        job_skills: List[Dict[str, Any]],
        candidate_degree: Optional[str] = None,
        candidate_field: Optional[str] = None,
        candidate_education: Optional[str] = None,
        candidate_exp_years: float = 0.0,
        job_education_req: Optional[str] = None,
        job_exp_level: Optional[str] = None,
        candidate_remote_pref: Optional[str] = "any",
        candidate_pref_location: Optional[str] = None,
        candidate_interests: Optional[str] = None,
        job_remote: bool = False,
        job_location: str = "",
        job_category: str = "",
        job_id: int = 0
    ) -> Dict[str, Any]:
        """
        Executes complete Explainable Career Matching pipeline.
        Produces deterministic breakdown and genuine justifications.
        """
        # 1. Semantic Similarity
        raw_semantic = embedding_service.calculate_similarity(candidate_embedding, job_embedding)
        # Scaled non-linear curve to reflect realistic text similarity distribution of MiniLM
        # MiniLM cosine similarity typically clusters between 0.35 and 0.85 for tech job descriptions
        semantic_norm = min(1.0, max(0.0, (raw_semantic - 0.20) / 0.70))

        # 2. Skill Match
        skill_score, matched_skills, missing_skills = self.compute_skill_match(
            candidate_skills, job_skills
        )

        # 3. Eligibility Match
        eligibility_score, eligibility_reasons = self.compute_eligibility_match(
            candidate_degree, candidate_field, candidate_education,
            candidate_exp_years, job_education_req, job_exp_level
        )

        # 4. Preference Match
        preference_score, preference_reasons = self.compute_preference_match(
            candidate_remote_pref, candidate_pref_location, candidate_interests,
            job_remote, job_location, job_category
        )

        # 5. Hybrid Weighted Score
        final_score = (
            self.semantic_weight * semantic_norm +
            self.skill_weight * skill_score +
            self.eligibility_weight * eligibility_score +
            self.preference_weight * preference_score
        )
        final_score = min(1.0, max(0.0, final_score))

        # Convert to clean percentages
        overall_match = int(round(final_score * 100))
        semantic_match = int(round(semantic_norm * 100))
        skill_match = int(round(skill_score * 100))
        eligibility_match = int(round(eligibility_score * 100))
        preference_match = int(round(preference_score * 100))

        # 6. Generate Explainability Justifications from actual metrics
        explanation: List[str] = []

        if skill_match >= 80:
            explanation.append(f"Strong overlap with technical skills ({len(matched_skills)} matched).")
        elif skill_match >= 50:
            explanation.append(f"Moderate skill overlap with foundational competencies ({', '.join(matched_skills[:3])}).")
        else:
            explanation.append("Developing skill alignment with opportunities for focused learning.")

        if eligibility_reasons:
            explanation.append(eligibility_reasons[0])

        if semantic_match >= 75:
            explanation.append("Your profile has high contextual and semantic similarity to this role.")
        elif semantic_match >= 50:
            explanation.append("Good conceptual alignment with the team's project scope.")

        if preference_reasons:
            explanation.append(preference_reasons[0])

        return {
            "job_id": job_id,
            "overall_match": overall_match,
            "semantic_match": semantic_match,
            "skill_match": skill_match,
            "eligibility_match": eligibility_match,
            "preference_match": preference_match,
            "matching_skills": matched_skills,
            "missing_skills": missing_skills,
            "explanation": explanation
        }

matching_engine = ExplainableMatchingEngine()
