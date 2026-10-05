from typing import List, Dict, Any, Optional
from collections import Counter
from app.ml.skill_extractor import skill_extractor
from app.schemas.skill_gap import SkillGapResponse, MissingSkillDetail

class SkillGapEngine:
    """
    Skill Gap Analysis Engine for JobTrail-AI.
    Analyzes candidate skillset against a specific job or target career recommendations.
    Provides categorized skill gap metrics, frequency priority, and actionable career guidance.
    """

    def analyze_job_skill_gap(
        self,
        candidate_skills: List[str],
        job_skills: List[Dict[str, Any]],
        job_id: Optional[int] = None,
        job_title: Optional[str] = None
    ) -> SkillGapResponse:
        cand_norm_map = {skill_extractor.normalize_skill(s).lower(): s for s in candidate_skills}
        
        already_have = []
        missing = []
        missing_details = []

        for item in job_skills:
            skill_name = item.get("name", "")
            norm = skill_extractor.normalize_skill(skill_name)
            is_req = item.get("required", True)
            imp = float(item.get("importance", 1.0))
            category = skill_extractor.get_category(norm)

            if norm.lower() in cand_norm_map:
                already_have.append(norm)
            else:
                missing.append(norm)
                priority = "High" if (is_req or imp > 1.2) else "Medium"
                missing_details.append(
                    MissingSkillDetail(
                        skill=norm,
                        frequency_in_target_roles=1,
                        priority=priority,
                        category=category
                    )
                )

        total = len(already_have) + len(missing)
        readiness = int(round((len(already_have) / total * 100))) if total > 0 else 100

        if not missing:
            insight = f"You possess 100% of the required technical skills for {job_title or 'this role'}. Focus on presenting strong project implementations."
        else:
            top_missing = missing[:3]
            insight = f"Adding {', '.join(top_missing)} would directly bridge your skill gap and enhance your competitiveness for {job_title or 'this position'}."

        return SkillGapResponse(
            target_job_id=job_id,
            target_job_title=job_title,
            already_have=already_have,
            missing=missing,
            missing_details=missing_details,
            career_insight=insight,
            readiness_score=readiness
        )

    def analyze_aggregate_skill_gap(
        self,
        candidate_skills: List[str],
        top_jobs_skills: List[List[Dict[str, Any]]],
        target_role_domain: str = "your recommended roles"
    ) -> SkillGapResponse:
        """
        Aggregate skill gap across multiple top recommended roles.
        """
        cand_norm_set = {skill_extractor.normalize_skill(s).lower() for s in candidate_skills}
        all_already_have = set()
        missing_counter = Counter()

        for j_skills in top_jobs_skills:
            for item in j_skills:
                norm = skill_extractor.normalize_skill(item.get("name", ""))
                if norm.lower() in cand_norm_set:
                    all_already_have.add(norm)
                else:
                    missing_counter[norm] += 1

        missing_details: List[MissingSkillDetail] = []
        for skill_name, freq in missing_counter.most_common():
            priority = "High" if freq >= 2 else "Medium"
            category = skill_extractor.get_category(skill_name)
            missing_details.append(
                MissingSkillDetail(
                    skill=skill_name,
                    frequency_in_target_roles=freq,
                    priority=priority,
                    category=category
                )
            )

        missing_sorted = [d.skill for d in missing_details]
        total_unique = len(all_already_have) + len(missing_sorted)
        readiness = int(round(len(all_already_have) / total_unique * 100)) if total_unique > 0 else 100

        if missing_sorted:
            top_3 = missing_sorted[:3]
            insight = f"Across {target_role_domain}, high-frequency gaps include {', '.join(top_3)}. Mastering these will yield the highest match score lift."
        else:
            insight = f"You hold comprehensive coverage across your top target roles."

        return SkillGapResponse(
            target_job_id=None,
            target_job_title=f"Top Recommended Roles ({len(top_jobs_skills)} analyzed)",
            already_have=sorted(list(all_already_have)),
            missing=missing_sorted,
            missing_details=missing_details,
            career_insight=insight,
            readiness_score=readiness
        )

skill_gap_engine = SkillGapEngine()
