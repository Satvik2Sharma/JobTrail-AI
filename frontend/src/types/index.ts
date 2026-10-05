export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'candidate' | 'recruiter';
}

export interface SkillItem {
  id: number;
  name: string;
  category?: string;
  proficiency: string;
  source: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  full_name: string;
  email: string;
  role: string;
  phone?: string;
  location?: string;
  preferred_location?: string;
  remote_preference: string;
  education?: string;
  degree?: string;
  field_of_study?: string;
  graduation_year?: number;
  experience_years: number;
  interests?: string;
  resume_filename?: string;
  profile_completeness: number;
  skills: SkillItem[];
  extracted_data?: Record<string, any>;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  employment_type: string;
  experience_level: string;
  education_requirement?: string;
  category: string;
  description: string;
  requirements?: string;
  responsibilities?: string;
  salary_min?: number;
  salary_max?: number;
  application_url?: string;
  skills: string[];
  is_saved: boolean;
  has_applied: boolean;
  application_status?: string;
  created_at?: string;
}

export interface ExplainableMatch {
  job_id: number;
  overall_match: number;
  semantic_match: number;
  skill_match: number;
  eligibility_match: number;
  preference_match: number;
  matching_skills: string[];
  missing_skills: string[];
  explanation: string[];
}

export interface JobRecommendationItem {
  job: Job;
  match: ExplainableMatch;
}

export interface RecommendationListResponse {
  total_matches: number;
  items: JobRecommendationItem[];
}

export interface MissingSkillDetail {
  skill: string;
  frequency_in_target_roles: number;
  priority: 'High' | 'Medium' | 'Low';
  category?: string;
}

export interface SkillGapResponse {
  target_job_id?: number;
  target_job_title?: string;
  already_have: string[];
  missing: string[];
  missing_details: MissingSkillDetail[];
  career_insight: string;
  readiness_score: number;
}

export interface Application {
  id: number;
  user_id: number;
  job_id: number;
  status: 'saved' | 'applied' | 'interview' | 'rejected' | 'selected';
  notes?: string;
  applied_at: string;
  updated_at?: string;
  job: Job;
}

export interface CandidateRankingItem {
  candidate_id: number;
  candidate_name: string;
  candidate_email: string;
  degree?: string;
  experience_years: number;
  match: ExplainableMatch;
}
