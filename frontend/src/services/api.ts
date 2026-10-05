import {
  User,
  UserProfile,
  Job,
  ExplainableMatch,
  RecommendationListResponse,
  SkillGapResponse,
  Application,
  CandidateRankingItem
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('jobtrail_token');
  }

  public setToken(token: string): void {
    localStorage.setItem('jobtrail_token', token);
  }

  public removeToken(): void {
    localStorage.removeItem('jobtrail_token');
    localStorage.removeItem('jobtrail_user');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.removeToken();
      // Only redirect if not already on login or register or landing
      const path = window.location.pathname;
      if (path !== '/login' && path !== '/register' && path !== '/') {
        window.location.href = '/login';
      }
    }

    if (!response.ok) {
      let errorMsg = `Request failed: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        errorMsg = errorJson.detail || errorJson.message || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    }

    // Return empty object for 204 or empty responses
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // --- Auth API ---
  async login(email: string, password: string): Promise<{ access_token: string; token_type: string; user: User }> {
    const data = await this.request<{ access_token: string; token_type: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    localStorage.setItem('jobtrail_user', JSON.stringify(data.user));
    return data;
  }

  async register(email: string, password: string, full_name: string, role: string = 'candidate'): Promise<{ access_token: string; token_type: string; user: User }> {
    const data = await this.request<{ access_token: string; token_type: string; user: User }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, role }),
    });
    this.setToken(data.access_token);
    localStorage.setItem('jobtrail_user', JSON.stringify(data.user));
    return data;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/api/auth/logout', { method: 'POST' });
    } finally {
      this.removeToken();
    }
  }

  async getMe(): Promise<User> {
    return this.request<User>('/api/auth/me');
  }

  // --- Profile API ---
  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>('/api/profile');
  }

  async updateProfile(profileData: Omit<Partial<UserProfile>, 'skills'> & { skills?: string[] }): Promise<UserProfile> {
    return this.request<UserProfile>('/api/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async addSkill(name: string, proficiency = 'intermediate', source = 'manual'): Promise<any> {
    return this.request('/api/profile/skills', {
      method: 'POST',
      body: JSON.stringify({ name, proficiency, source }),
    });
  }

  async removeSkill(skillName: string): Promise<any> {
    return this.request(`/api/profile/skills/${encodeURIComponent(skillName)}`, {
      method: 'DELETE',
    });
  }

  // --- Resume Intelligence API ---
  async uploadResume(file: File): Promise<{
    status: string;
    message: string;
    filename: string;
    intelligence: any;
    skills_detected_count: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/api/resume/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async getResumeIntelligence(): Promise<{
    has_resume: boolean;
    filename?: string;
    intelligence?: any;
    completeness?: number;
  }> {
    return this.request('/api/resume');
  }

  // --- Jobs API ---
  async listJobs(params: {
    page?: number;
    page_size?: number;
    category?: string;
    remote?: boolean;
    location?: string;
    employment_type?: string;
    experience_level?: string;
    keyword?: string;
  } = {}): Promise<{ total: number; page: number; page_size: number; total_pages: number; items: Job[] }> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    if (params.category && params.category !== 'all') searchParams.append('category', params.category);
    if (params.remote !== undefined) searchParams.append('remote', params.remote.toString());
    if (params.location) searchParams.append('location', params.location);
    if (params.employment_type && params.employment_type !== 'all') searchParams.append('employment_type', params.employment_type);
    if (params.experience_level && params.experience_level !== 'all') searchParams.append('experience_level', params.experience_level);
    if (params.keyword) searchParams.append('keyword', params.keyword);

    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request(`/api/jobs${query}`);
  }

  async getJob(id: number): Promise<Job> {
    return this.request<Job>(`/api/jobs/${id}`);
  }

  async saveJob(id: number): Promise<{ message: string; saved: boolean }> {
    return this.request(`/api/jobs/${id}/save`, { method: 'POST' });
  }

  async unsaveJob(id: number): Promise<{ message: string; saved: boolean }> {
    return this.request(`/api/jobs/${id}/save`, { method: 'DELETE' });
  }

  async getSavedJobs(): Promise<{ total: number; items: Job[] }> {
    return this.request('/api/saved-jobs');
  }

  async applyToJob(id: number, notes?: string): Promise<Application> {
    return this.request<Application>(`/api/jobs/${id}/apply`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  // --- Recommendations API ---
  async getRecommendations(params: {
    limit?: number;
    min_match_score?: number;
    category?: string;
  } = {}): Promise<RecommendationListResponse> {
    const searchParams = new URLSearchParams();
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.min_match_score) searchParams.append('min_match_score', params.min_match_score.toString());
    if (params.category && params.category !== 'all') searchParams.append('category', params.category);

    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<RecommendationListResponse>(`/api/recommendations${query}`);
  }

  async getJobMatch(id: number): Promise<ExplainableMatch> {
    return this.request<ExplainableMatch>(`/api/jobs/${id}/match`);
  }

  // --- Semantic Search API ---
  async semanticSearch(q: string, category?: string, remote?: boolean, limit = 20): Promise<{
    query: string;
    total_matches: number;
    items: Array<{ job: Job; relevance_score: number; raw_similarity: number }>;
  }> {
    const searchParams = new URLSearchParams();
    searchParams.append('q', q);
    searchParams.append('limit', limit.toString());
    if (category && category !== 'all') searchParams.append('category', category);
    if (remote !== undefined) searchParams.append('remote', remote.toString());

    return this.request(`/api/search?${searchParams.toString()}`);
  }

  // --- Skill Gap API ---
  async getSkillGap(jobId?: number): Promise<SkillGapResponse> {
    const query = jobId ? `?job_id=${jobId}` : '';
    return this.request<SkillGapResponse>(`/api/skill-gap${query}`);
  }

  // --- Application Tracker API ---
  async getApplications(): Promise<Application[]> {
    return this.request<Application[]>('/api/applications');
  }

  async updateApplicationStatus(id: number, status: string, notes?: string): Promise<Application> {
    return this.request<Application>(`/api/applications/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status, notes }),
    });
  }

  // --- Recruiter API ---
  async createRecruiterJob(data: any): Promise<Job> {
    return this.request<Job>('/api/recruiter/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getRecruiterJobs(): Promise<Job[]> {
    return this.request<Job[]>('/api/recruiter/jobs');
  }

  async rankCandidates(jobId: number): Promise<CandidateRankingItem[]> {
    return this.request<CandidateRankingItem[]>(`/api/recruiter/jobs/${jobId}/candidates`);
  }
}

export const api = new ApiClient();
