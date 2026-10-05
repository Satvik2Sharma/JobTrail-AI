# JobTrail-AI — REST API Reference

JobTrail-AI exposes a comprehensive RESTful API built on FastAPI. Interactive Swagger documentation is accessible locally at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/register`
Creates a new candidate or recruiter account.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!",
    "full_name": "Satvik Sharma",
    "role": "candidate"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Satvik Sharma",
      "role": "candidate"
    }
  }
  ```

### `POST /api/auth/login`
Authenticates user credentials and returns JWT bearer token.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!"
  }
  ```
- **Response `200 OK`**: Same token schema as register.

### `POST /api/auth/logout`
Client-side token disposal confirmation.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: `{"message": "Successfully logged out.", "status": "ok"}`

### `GET /api/auth/me`
Retrieves currently authenticated user record.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**: User profile object.

---

## 2. Profile Management (`/api/profile`)

### `GET /api/profile`
Fetches complete candidate profile, verified skills, and dynamically calculated profile completeness score.
- **Headers**: `Authorization: Bearer <token>`
- **Response `200 OK`**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "full_name": "Satvik Sharma",
    "email": "demo@jobtrail.local",
    "role": "candidate",
    "phone": "+1 (555) 234-5678",
    "location": "San Francisco, CA",
    "preferred_location": "San Francisco, CA",
    "remote_preference": "hybrid",
    "education": "B.Tech",
    "degree": "B.Tech Computer Science",
    "field_of_study": "Computer Science",
    "graduation_year": 2025,
    "experience_years": 0.5,
    "interests": "Machine Learning, Backend Systems",
    "profile_completeness": 95,
    "skills": [
      {
        "id": 1,
        "name": "Python",
        "category": "Programming Languages",
        "proficiency": "advanced",
        "source": "manual"
      }
    ]
  }
  ```

### `PUT /api/profile`
Updates profile metadata and synchronized skills array.

### `POST /api/profile/skills`
Attaches an individual skill with proficiency (`beginner`, `intermediate`, `advanced`).

### `DELETE /api/profile/skills/{skill_name}`
Detaches a skill from the candidate profile.

---

## 3. Resume Intelligence (`/api/resume`)

### `POST /api/resume/upload`
Uploads a candidate PDF resume (`multipart/form-data`).
- Extracts text via PyMuPDF.
- Extracts name, email, phone, education, degree, field of study, graduation year.
- Matches and normalizes technical skills against canonical taxonomy.
- Updates candidate profile automatically.
- **Response `200 OK`**:
  ```json
  {
    "status": "completed",
    "message": "Resume successfully parsed and intelligence extracted.",
    "filename": "resume_abc123_satvik_sharma.pdf",
    "intelligence": {
      "name": "Satvik Sharma",
      "email": "satvik.sharma@example.com",
      "phone": "+1 (555) 234-5678",
      "degree": "B.Tech in Computer Science",
      "detected_skills": ["Python", "FastAPI", "Machine Learning", "Docker"],
      "profile_completeness": 100
    },
    "skills_detected_count": 36
  }
  ```

### `GET /api/resume`
Returns the status, parsed intelligence, and completeness of the candidate's active resume.

---

## 4. Jobs & Saved Bookmarks (`/api/jobs`, `/api/saved-jobs`)

### `GET /api/jobs`
Lists job openings with query filters:
- Parameters: `page`, `page_size`, `category`, `remote`, `location`, `employment_type`, `experience_level`, `keyword`.
- Response includes `is_saved` and `has_applied` status for the authenticated user.

### `GET /api/jobs/{id}`
Retrieves full job details, company information, required skills, and duties.

### `POST /api/jobs/{id}/save` & `DELETE /api/jobs/{id}/save`
Bookmarks or removes an opportunity from saved listings.

### `GET /api/saved-jobs`
Retrieves all bookmarked opportunities for the current candidate.

---

## 5. Explainable Recommendations (`/api/recommendations`)

### `GET /api/recommendations`
Returns personalized opportunities sorted by the hybrid recommendation engine.
- Parameters: `limit` (default: 30), `min_match_score` (default: 0), `category`.
- **Response `200 OK`**:
  ```json
  {
    "total_matches": 47,
    "items": [
      {
        "job": {
          "id": 12,
          "title": "Machine Learning Intern",
          "company": "NeuralPath Labs"
        },
        "match": {
          "job_id": 12,
          "overall_match": 94,
          "semantic_match": 92,
          "skill_match": 96,
          "eligibility_match": 100,
          "preference_match": 85,
          "matching_skills": ["Python", "Machine Learning", "Pandas", "SQL"],
          "missing_skills": ["Docker"],
          "explanation": [
            "Strong overlap with technical skills (4 matched).",
            "Your degree and field of study fully satisfy educational requirements.",
            "Your profile has high contextual and semantic similarity to this role.",
            "Remote flexibility matches your remote work preference."
          ]
        }
      }
    ]
  }
  ```

### `GET /api/jobs/{id}/match`
Detailed 4-factor explainable match breakdown for a specific job.

---

## 6. Semantic Search (`/api/search`)

### `GET /api/search`
Natural language semantic search powered by Sentence-Transformers.
- Parameters: `q` (e.g. `"machine learning internship for python student with no experience"`), `category`, `remote`, `limit`.
- Returns jobs ranked by vector cosine similarity combined with keyword matching boosts.

---

## 7. Skill Gap Analysis (`/api/skill-gap`)

### `GET /api/skill-gap`
Analyzes skill gaps against:
- A specific job (via `?job_id=X`), OR
- Aggregated across the candidate's top 5 recommended opportunities.
- **Response `200 OK`**:
  ```json
  {
    "target_job_id": 12,
    "target_job_title": "Machine Learning Intern at NeuralPath Labs",
    "already_have": ["Python", "Machine Learning", "Pandas", "SQL"],
    "missing": ["Docker", "AWS"],
    "missing_details": [
      {
        "skill": "Docker",
        "frequency_in_target_roles": 1,
        "priority": "High",
        "category": "Cloud & DevOps"
      }
    ],
    "career_insight": "Adding Docker and AWS would directly bridge your skill gap and enhance your competitiveness.",
    "readiness_score": 67
  }
  ```

---

## 8. Application Tracking (`/api/applications`)

### `POST /api/jobs/{id}/apply`
Submits application and logs initial status `applied`.

### `GET /api/applications`
Retrieves candidate's application history with statuses (`applied`, `interview`, `selected`, `rejected`).

### `PUT /api/applications/{id}`
Updates status or notes for an application.

---

## 9. Recruiter Operations (`/api/recruiter`)

### `POST /api/recruiter/jobs`
Recruiter posts a new job. Generates embeddings on insertion.

### `GET /api/recruiter/jobs`
Lists jobs created by the authenticated recruiter.

### `GET /api/recruiter/jobs/{id}/candidates`
Ranks candidate pool against the job opening using the identical explainable ML engine.
