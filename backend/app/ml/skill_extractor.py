import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple

class SkillExtractor:
    """
    Skill taxonomy and extraction engine for JobTrail-AI.
    Provides case-insensitive normalized matching, alias handling,
    and regex word-boundary detection to avoid false substring positives.
    """
    def __init__(self, taxonomy_path: Optional[str] = None):
        if not taxonomy_path:
            # Default to data/skills.json in project root
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            taxonomy_path = str(base_dir / "data" / "skills.json")
        
        self.taxonomy_path = taxonomy_path
        self.skills_by_normalized: Dict[str, str] = {} # normalized -> canonical
        self.skills_by_alias: Dict[str, str] = {} # lowercase alias -> canonical
        self.canonical_skills: Set[str] = set()
        self.skill_categories: Dict[str, str] = {}
        self.short_skills = {"c", "r", "go", "ai", "ml", "dl", "cv", "nlp", "ts", "js", "sql"}
        self._load_taxonomy()

    def _load_taxonomy(self):
        try:
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for item in data:
                canonical = item["name"].strip()
                category = item.get("category", "Technical")
                self.canonical_skills.add(canonical)
                self.skills_by_normalized[canonical.lower()] = canonical
                self.skill_categories[canonical] = category

                # Aliases
                for alias in item.get("aliases", []):
                    clean_alias = alias.strip().lower()
                    self.skills_by_alias[clean_alias] = canonical
                    
        except Exception as e:
            print(f"[SkillExtractor] Warning: Could not load taxonomy from {self.taxonomy_path}: {e}")

    def normalize_skill(self, raw_skill: str) -> str:
        """Returns the canonical skill name or cleaned input."""
        cleaned = raw_skill.strip()
        cleaned_lower = cleaned.lower()

        if cleaned_lower in self.skills_by_alias:
            return self.skills_by_alias[cleaned_lower]
        if cleaned_lower in self.skills_by_normalized:
            return self.skills_by_normalized[cleaned_lower]
        
        # Handle some common prefixes/suffixes
        cleaned_suffix = re.sub(r'[\s\.\-]+(?:js|framework|library)$', '', cleaned_lower)
        if cleaned_suffix in self.skills_by_alias:
            return self.skills_by_alias[cleaned_suffix]

        return cleaned

    def get_category(self, skill_name: str) -> str:
        canonical = self.normalize_skill(skill_name)
        return self.skill_categories.get(canonical, "Technical")

    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Scans text for skills from the taxonomy using robust token boundary matching.
        Avoids substring false positives.
        """
        if not text:
            return []

        found_skills: Set[str] = set()
        normalized_text = f" {text.lower()} "

        # 1. Multi-word and phrase matching first
        for alias, canonical in sorted(self.skills_by_alias.items(), key=lambda x: len(x[0]), reverse=True):
            if " " in alias or "-" in alias or "+" in alias or "." in alias or "#" in alias:
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, normalized_text):
                    found_skills.add(canonical)

        # 2. Token based matching for single-word skills
        tokens = re.findall(r'[a-zA-Z0-9\+\#\.\-]+', text)
        for token in tokens:
            token_clean = token.strip(".,;:()[]{}").lower()
            if not token_clean:
                continue

            # Short tokens (like 'c', 'r') require special care
            if token_clean in self.short_skills:
                # Require exact boundary in original text
                exact_pat = r'(?<![a-zA-Z0-9])' + re.escape(token.strip(".,;:()[]{}")) + r'(?![a-zA-Z0-9])'
                if re.search(exact_pat, text):
                    canonical = self.skills_by_alias.get(token_clean) or self.skills_by_normalized.get(token_clean)
                    if canonical:
                        found_skills.add(canonical)
            else:
                if token_clean in self.skills_by_alias:
                    found_skills.add(self.skills_by_alias[token_clean])
                elif token_clean in self.skills_by_normalized:
                    found_skills.add(self.skills_by_normalized[token_clean])

        return sorted(list(found_skills))

skill_extractor = SkillExtractor()
