import os
import re
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from app.resume.parser_base import BaseResumeParser
from app.resume.pymupdf_parser import PyMuPDFResumeParser
from app.ml.skill_extractor import skill_extractor
from app.core.config import settings

class ResumeService:
    """
    Resume Intelligence service extracting candidate profile, normalized skills,
    and structured attributes from uploaded resumes.
    """

    def __init__(self, parser: Optional[BaseResumeParser] = None):
        self.parser = parser or PyMuPDFResumeParser()

    def save_uploaded_file(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Validates and safely saves an uploaded PDF resume to disk.
        Returns: (safe_filename, absolute_path)
        """
        # Validate extension
        clean_ext = os.path.splitext(original_filename)[1].lower()
        if clean_ext != ".pdf":
            raise ValueError("Only PDF documents (.pdf) are supported.")

        # Validate size
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB.")

        # Ensure directory exists
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique safe filename
        safe_filename = f"resume_{uuid.uuid4().hex[:12]}_{re.sub(r'[^a-zA-Z0-9_\.]', '_', original_filename)}"
        target_path = upload_dir / safe_filename

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return safe_filename, str(target_path)

    def extract_text_from_file(self, file_path: str) -> str:
        return self.parser.extract_text(file_path)

    def parse_resume_intelligence(self, raw_text: str) -> Dict[str, Any]:
        """
        Extracts candidate details, education, degree, experience, projects,
        and normalized skills from raw resume text without hallucination.
        """
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        # 1. Contact Info
        email = None
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
        if email_match:
            email = email_match.group(0).lower()

        phone = None
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', raw_text)
        if phone_match and len(phone_match.group(0).replace(" ", "").replace("-", "")) >= 10:
            phone = phone_match.group(0)

        # Extract Name from top lines (skipping titles or labels)
        candidate_name = None
        for line in lines[:5]:
            if "@" in line or "resume" in line.lower() or "curriculum" in line.lower():
                continue
            if len(line.split()) in [2, 3, 4] and re.match(r'^[A-Za-z\s\.\-]+$', line):
                candidate_name = line.strip()
                break

        # 2. Education & Degree
        degree = None
        field = None
        education_level = None
        grad_year = None

        text_lower = raw_text.lower()
        if "b.tech" in text_lower or "btech" in text_lower or "b.e" in text_lower:
            education_level = "B.Tech / B.E."
            degree = "B.Tech in Computer Science" if "computer science" in text_lower or "cse" in text_lower else "B.Tech"
        elif "m.tech" in text_lower or "mtech" in text_lower or "master" in text_lower or "m.s." in text_lower:
            education_level = "Master's"
            degree = "M.Tech / M.S. in Computer Science" if "computer science" in text_lower else "Master's Degree"
        elif "bachelor" in text_lower or "b.s." in text_lower or "b.sc" in text_lower:
            education_level = "Bachelor's"
            degree = "Bachelor of Science"

        if "computer science" in text_lower or "cse" in text_lower:
            field = "Computer Science"
        elif "information technology" in text_lower or " it " in text_lower:
            field = "Information Technology"
        elif "data science" in text_lower:
            field = "Data Science"
        elif "artificial intelligence" in text_lower or " ai " in text_lower:
            field = "Artificial Intelligence"
        elif "electrical" in text_lower:
            field = "Electrical Engineering"

        # Graduation year check (e.g. 2020-2029)
        year_matches = re.findall(r'\b(20[12][0-9])\b', raw_text)
        if year_matches:
            # Typically highest year indicates graduation or expected graduation
            candidate_years = [int(y) for y in year_matches if 2018 <= int(y) <= 2030]
            if candidate_years:
                grad_year = max(candidate_years)

        # 3. Skills extraction via normalized taxonomy
        detected_skills = skill_extractor.extract_skills_from_text(raw_text)

        # 4. Experience estimation
        exp_years = 0.0
        exp_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience', text_lower)
        if exp_match:
            try:
                exp_years = float(exp_match.group(1))
            except ValueError:
                exp_years = 0.0
        elif "intern" in text_lower or "fresher" in text_lower or "student" in text_lower:
            exp_years = 0.5
        elif "junior" in text_lower:
            exp_years = 1.0

        # 5. Extract Section Headings & Project Snippets
        sections = self._extract_sections(raw_text)

        # 6. Profile Completeness Calculation
        completeness = self.calculate_completeness(
            name=candidate_name,
            email=email,
            phone=phone,
            degree=degree,
            field=field,
            skills=detected_skills,
            experience_years=exp_years,
            projects=sections.get("projects", [])
        )

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "education": education_level,
            "degree": degree,
            "field_of_study": field,
            "graduation_year": grad_year,
            "experience_years": exp_years,
            "detected_skills": detected_skills,
            "sections": sections,
            "profile_completeness": completeness,
            "raw_text_length": len(raw_text)
        }

    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """Splits resume into logical sections based on common headings."""
        sections = {"projects": [], "experience": [], "certifications": [], "education": []}
        current_section = None
        current_items = []

        heading_patterns = {
            "projects": re.compile(r'^(projects|academic projects|technical projects)', re.I),
            "experience": re.compile(r'^(experience|work experience|employment|internships)', re.I),
            "certifications": re.compile(r'^(certifications|certificates|licenses)', re.I),
            "education": re.compile(r'^(education|academics|qualifications)', re.I),
        }

        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue

            matched_sec = None
            for sec_name, pattern in heading_patterns.items():
                if pattern.match(line_str) and len(line_str) < 35:
                    matched_sec = sec_name
                    break

            if matched_sec:
                if current_section and current_items:
                    sections[current_section].extend(current_items[:5])
                current_section = matched_sec
                current_items = []
            elif current_section:
                if len(line_str) > 10:
                    current_items.append(line_str)

        if current_section and current_items:
            sections[current_section].extend(current_items[:5])

        return sections

    def calculate_completeness(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        degree: Optional[str],
        field: Optional[str],
        skills: List[str],
        experience_years: float,
        projects: List[str]
    ) -> int:
        """
        Calculates deterministic percentage (0-100) based on actual present fields:
        - Name: 10%
        - Email: 15%
        - Phone: 10%
        - Degree/Education: 20%
        - Field of study: 10%
        - Skills (>=3 skills): 20%
        - Experience / Projects: 15%
        """
        score = 0
        if name and name.strip():
            score += 10
        if email and email.strip():
            score += 15
        if phone and phone.strip():
            score += 10
        if degree and degree.strip():
            score += 20
        if field and field.strip():
            score += 10
        if len(skills) >= 5:
            score += 20
        elif len(skills) >= 1:
            score += 10
        if experience_years > 0 or len(projects) > 0:
            score += 15

        return min(100, score)

resume_service = ResumeService()
