import os
import re
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from app.resume.parser_base import BaseResumeParser
from app.resume.pymupdf_parser import PyMuPDFResumeParser
from app.ml.skill_extractor import skill_extractor
from app.core.config import settings

class ResumeService:
    """
    Resume Intelligence service extracting candidate profile, normalized skills,
    and structured attributes from uploaded resumes without hallucinations.
    """

    def __init__(self, parser: Optional[BaseResumeParser] = None):
        self.parser = parser or PyMuPDFResumeParser()

    def validate_uploaded_file(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: Optional[str] = None
    ):
        """
        Validates the uploaded file extension, MIME type, size, and header.
        Raises ValueError if invalid.
        """
        if not original_filename:
            raise ValueError("Filename is required.")

        # Check file extension
        clean_ext = os.path.splitext(original_filename)[1].lower()
        if clean_ext != ".pdf":
            raise ValueError("Invalid file format. Only PDF documents (.pdf) are supported.")

        # Check MIME type if provided
        if content_type and content_type.lower() not in ("application/pdf", "application/x-pdf", "application/octet-stream"):
            raise ValueError(f"Invalid Content-Type '{content_type}'. Must be 'application/pdf'.")

        # Check file size
        if len(file_bytes) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise ValueError(f"File size exceeds limit of {max_mb}MB.")

        # Check PDF magic bytes (%PDF-)
        if not file_bytes.startswith(b"%PDF-"):
            raise ValueError("Corrupted or invalid PDF header. File is not a valid PDF document.")

    def sanitize_filename(self, filename: str) -> str:
        """Sanitizes filename against path traversal and special characters."""
        base_name = os.path.basename(filename)
        # Remove any path traversal tokens
        clean = re.sub(r'[^a-zA-Z0-9_\.-]', '_', base_name)
        # Ensure it has .pdf extension
        if not clean.lower().endswith(".pdf"):
            clean = f"{clean}.pdf"
        return clean

    def generate_storage_path(
        self,
        user_id: int,
        resume_id: int,
        original_filename: str
    ) -> Tuple[str, str]:
        """
        Generates safe filename and object path adhering to:
        users/{user_id}/resumes/{resume_id}/{safe_filename}
        """
        safe_filename = self.sanitize_filename(original_filename)
        storage_path = f"users/{user_id}/resumes/{resume_id}/{safe_filename}"
        return safe_filename, storage_path

    def extract_text(self, file_input: Union[str, Path, bytes]) -> str:
        """Extracts text from file path or raw bytes via PyMuPDF."""
        return self.parser.extract_text(file_input)

    def extract_text_from_file(self, file_path: str) -> str:
        """Backward-compatible helper for file paths."""
        return self.extract_text(file_path)

    def save_uploaded_file(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Legacy local file helper preserved for backward compatibility in tests.
        Returns: (safe_filename, absolute_path)
        """
        self.validate_uploaded_file(file_bytes, original_filename)

        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = f"resume_{uuid.uuid4().hex[:12]}_{self.sanitize_filename(original_filename)}"
        target_path = upload_dir / safe_filename

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return safe_filename, str(target_path)

    def parse_resume_intelligence(self, raw_text: str) -> Dict[str, Any]:
        """
        Extracts structured candidate information:
        - name, email, phone, location
        - education, degree, field_of_study, graduation_year, CGPA
        - experience, internships, projects, research/publications, certifications
        - technical skills (canonical + raw mappings), soft skills, interests
        - profile completeness
        """
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        text_lower = raw_text.lower()

        # 1. Contact Information
        email = None
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
        if email_match:
            email = email_match.group(0).lower()

        phone = None
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', raw_text)
        if phone_match and len(phone_match.group(0).replace(" ", "").replace("-", "")) >= 10:
            phone = phone_match.group(0).strip()

        # Location detection (e.g. San Francisco, CA | New York, NY | Roorkee, Uttarakhand)
        location = None
        location_patterns = [
            r'([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})\b',  # City, ST
            r'([A-Z][a-zA-Z\s]+,\s*(?:USA|United States|India|Canada|UK|Germany|Singapore|Uttarakhand|Delhi|Maharashtra|Karnataka))\b',
            r'\b([A-Z][a-z]+,\s*[A-Z][a-z]+)\b',
        ]
        # Search among top header lines
        header_text = " | ".join(lines[:6])
        for pat in location_patterns:
            loc_match = re.search(pat, header_text)
            if loc_match:
                candidate_loc = loc_match.group(1).strip()
                if not any(skip in candidate_loc.lower() for skip in ["bachelor", "master", "university", "institute", "expected", "gpa", "technology"]):
                    location = candidate_loc
                    break

        # Candidate Name extraction (skipping titles, email, phone, links)
        candidate_name = None
        for line in lines[:5]:
            if "@" in line or "resume" in line.lower() or "curriculum" in line.lower() or "linkedin" in line.lower() or "http" in line.lower():
                continue
            cleaned_line = re.sub(r'[\|\•\-\:]', '', line).strip()
            tokens = cleaned_line.split()
            if 2 <= len(tokens) <= 4 and re.match(r'^[A-Za-z\s\.\-]+$', cleaned_line):
                candidate_name = cleaned_line
                break

        # Fallback for multi-column header lines containing embedded candidate names
        if not candidate_name:
            title_stopwords = {
                'developer', 'engineer', 'fullstack', 'frontend', 'backend', 'manager',
                'intern', 'student', 'undergraduate', 'portfolio', 'github', 'linkedin',
                'resume', 'cv', 'view', 'repository', 'live', 'uttarakhand', 'roorkee',
                'california', 'francisco', 'delhi', 'mumbai', 'india', 'york'
            }
            for line in lines[:5]:
                scrubbed = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' ', line)
                scrubbed = re.sub(r'https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com/\S+', ' ', scrubbed)
                scrubbed = re.sub(r'[^a-zA-Z\s]', ' ', scrubbed)
                words = [w for w in scrubbed.split() if w.lower() not in title_stopwords]
                matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b', ' '.join(words))
                valid_matches = [m for m in matches if not any(w.lower() in title_stopwords for w in m.split())]
                if valid_matches:
                    candidate_name = valid_matches[0].strip()
                    break

        # 2. Education, Degree, Field of Study, CGPA
        degree = None
        field = None
        education_level = None
        grad_year = None
        cgpa = None

        if "b.tech" in text_lower or "btech" in text_lower or "b.e" in text_lower:
            education_level = "B.Tech / B.E."
            degree = "B.Tech in Computer Science" if ("computer science" in text_lower or "cse" in text_lower) else "B.Tech"
        elif "m.tech" in text_lower or "mtech" in text_lower or "master" in text_lower or "m.s." in text_lower:
            education_level = "Master's"
            degree = "M.Tech / M.S. in Computer Science" if ("computer science" in text_lower or "cse" in text_lower) else "Master's Degree"
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

        # Graduation year check
        year_matches = re.findall(r'\b(20[12][0-9])\b', raw_text)
        if year_matches:
            candidate_years = [int(y) for y in year_matches if 2018 <= int(y) <= 2030]
            if candidate_years:
                grad_year = max(candidate_years)

        # CGPA / GPA detection
        cgpa = None
        cgpa_match = re.search(r'(?:GPA|CGPA|Score):\s*([0-9\.]+(?:\s*\/\s*[0-9\.]+)?)\b', raw_text, re.I)
        if cgpa_match:
            cgpa = cgpa_match.group(1).strip()
        else:
            cgpa_match = re.search(r'\b([0-9](?:\.[0-9]{1,2})?|10(?:\.0)?)\s*(?:CGPA|GPA)\b', raw_text, re.I)
            if cgpa_match:
                cgpa = cgpa_match.group(0).strip()
            else:
                cgpa_match = re.search(r'\b([\d\.]+\s*\/\s*(?:4\.0|10(?:\.0)?))\b', raw_text)
                if cgpa_match:
                    cgpa = cgpa_match.group(1).strip()

        # 3. Sections extraction (Projects, Experience, Certifications, Education, Research)
        sections = self._extract_sections(raw_text)

        # Internships extraction
        internships = []
        for exp_item in sections.get("experience", []):
            if "intern" in exp_item.lower():
                internships.append(exp_item)

        # Research / publications extraction
        research_publications = sections.get("research", [])
        if not research_publications:
            for exp_item in sections.get("experience", []):
                if any(w in exp_item.lower() for w in ["research", "paper", "publication", "lab", "conference"]):
                    research_publications.append(exp_item)

        # Projects
        projects = sections.get("projects", [])

        # Certifications
        certifications = sections.get("certifications", [])

        # 4. Experience estimation (Years)
        exp_years = 0.0
        exp_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience', text_lower)
        if exp_match:
            try:
                exp_years = float(exp_match.group(1))
            except ValueError:
                exp_years = 0.0
        elif len(internships) > 0 or "intern" in text_lower or "student" in text_lower:
            exp_years = 0.5
        elif "junior" in text_lower:
            exp_years = 1.0

        # 5. Skills extraction via normalized canonical taxonomy
        detected_skills = skill_extractor.extract_skills_from_text(raw_text)
        
        # Categorized skills & raw/normalized mappings
        technical_skills = []
        detailed_skills = []
        for s in detected_skills:
            detailed = skill_extractor.normalize_with_raw(s)
            detailed_skills.append(detailed)
            if detailed["category"] != "Soft Skills":
                technical_skills.append(detailed["normalized"])

        # Soft skills detection (if present in text)
        soft_skills_vocab = [
            "Communication", "Leadership", "Teamwork", "Problem Solving",
            "Critical Thinking", "Time Management", "Collaboration", "Adaptability"
        ]
        soft_skills = []
        for ss in soft_skills_vocab:
            if re.search(r'\b' + re.escape(ss.lower()) + r'\b', text_lower):
                soft_skills.append(ss)

        # Interests / Topics
        interests_match = re.search(r'•?\s*Interests:\s*([^\n]+)', raw_text, re.I)
        if interests_match:
            interests_list = [i.strip() for i in interests_match.group(1).split(',') if i.strip()]
        else:
            interests_list = []
            interests_vocab = ["Machine Learning", "Cloud Computing", "Distributed Systems", "Robotics", "Computer Vision", "Web Development", "AI Systems"]
            for it in interests_vocab:
                if it.lower() in text_lower:
                    interests_list.append(it)

        # 6. Profile Completeness Calculation
        completeness = self.calculate_completeness(
            name=candidate_name,
            email=email,
            phone=phone,
            degree=degree,
            field=field,
            skills=detected_skills,
            experience_years=exp_years,
            projects=projects,
            cgpa=cgpa,
            location=location
        )

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "location": location,
            "education": education_level,
            "degree": degree,
            "field_of_study": field,
            "graduation_year": grad_year,
            "cgpa": cgpa,
            "experience_years": exp_years,
            "experience": sections.get("experience", []),
            "internships": internships,
            "projects": projects,
            "research_publications": research_publications,
            "certifications": certifications,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "interests": interests_list,
            "detected_skills": detected_skills,
            "detected_skills_detailed": detailed_skills,
            "sections": sections,
            "profile_completeness": completeness,
            "raw_text_length": len(raw_text)
        }

    def _extract_sections(self, text: str) -> Dict[str, List[str]]:
        """Splits resume into logical sections based on common headings."""
        sections: Dict[str, List[str]] = {
            "projects": [],
            "experience": [],
            "certifications": [],
            "education": [],
            "research": []
        }
        current_section = None
        current_items = []

        heading_patterns = {
            "projects": re.compile(r'^(personal projects|projects|academic projects|technical projects|key projects)\b', re.I),
            "experience": re.compile(r'^(technical experience|work experience|experience|employment|internships)\b', re.I),
            "research": re.compile(r'^(research & publications|research and publications|research|publications)\b', re.I),
            "education_certs": re.compile(r'^(education\s+certifications|education\s*&?\s*certifications)\b', re.I),
            "certifications": re.compile(r'^(certifications|certificates|licenses)\b', re.I),
            "education": re.compile(r'^(education|academics|qualifications)\b', re.I),
            "interests": re.compile(r'^(hobbies & interests|hobbies and interests|interests|hobbies)\b', re.I),
        }

        for line in text.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue

            matched_sec = None
            for sec_name, pattern in heading_patterns.items():
                if pattern.match(line_str) and len(line_str) < 70:
                    matched_sec = sec_name
                    break

            if matched_sec:
                if current_section and current_items:
                    self._append_section_items(sections, current_section, current_items)
                current_section = matched_sec
                current_items = []
            elif current_section:
                if len(line_str) > 5:
                    current_items.append(line_str)

        if current_section and current_items:
            self._append_section_items(sections, current_section, current_items)

        return sections

    def _append_section_items(self, sections: Dict[str, List[str]], section_name: str, items: List[str]):
        """Helper to append items, handling two-column education/certifications."""
        if section_name == "education_certs":
            for item in items:
                # If multi-column (separated by 3+ spaces)
                cols = [c.strip() for c in re.split(r'\s{3,}', item) if c.strip()]
                for col in cols:
                    if any(k in col.lower() for k in ['workshop', 'certification', 'certificate', 'hackathon', 'udemy', 'oracle']):
                        sections["certifications"].append(col)
                    elif any(k in col.lower() for k in ['university', 'school', 'b.tech', 'class xii', 'class x', 'jee', 'cgpa', 'gpa']):
                        sections["education"].append(col)
                    else:
                        sections["education"].append(col)
        elif section_name in sections:
            sections[section_name].extend(items[:10])

    def calculate_completeness(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        degree: Optional[str],
        field: Optional[str],
        skills: List[str],
        experience_years: float,
        projects: List[str],
        cgpa: Optional[str] = None,
        location: Optional[str] = None
    ) -> int:
        """
        Calculates deterministic percentage (0-100) based on present fields:
        - Name: 10%
        - Email: 15%
        - Phone: 10%
        - Degree/Education: 15%
        - Field of study: 10%
        - CGPA / Location: 5%
        - Skills (>=5 skills): 20%
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
        if cgpa or location:
            score += 5

        return min(100, score)

resume_service = ResumeService()
