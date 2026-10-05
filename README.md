# JobTrail-AI

### Explainable AI-Powered Job & Internship Recommendation Platform

> **"Discover opportunities that match your profile — and understand exactly why."**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite%20%7C%20TypeScript-61DAFB?logo=react)](https://react.dev)
[![Sentence Transformers](https://img.shields.io/badge/ML-Sentence--Transformers%20(all--MiniLM--L6--v2)-FFA500)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?logo=tailwind-css)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/Tests-31%20Passed%20(100%25)-success)](backend/tests/)

---

## Academic Honesty & Disclosures

| Component | Technical Implementation & Reality |
|:---|:---|
| **Embedding Model** | Pretrained Sentence Transformer (`sentence-transformers/all-MiniLM-L6-v2`). *No custom transformer weights were fine-tuned or trained.* |
| **Recommendation Engine** | Custom deterministic 4-dimensional hybrid ranking pipeline with mathematical explainability. |
| **Similarity Metric** | Cosine similarity across normalized 384-dimensional dense vectors. |
| **Dataset** | 305 structured synthetic prototype job records across software engineering, AI/ML, and cloud roles. *Not scraped or live employer postings.* |
| **Resume Parser** | PyMuPDF (`fitz`) textual extraction with regex entity extraction and 107-skill canonical taxonomy normalization. |
| **Live Web Scraping** | *None.* The platform operates exclusively on curated, deterministic benchmark data for reproducibility. |

---

## Table of Contents

```text
JobTrail-AI
├── Overview
├── Problem
├── Solution
├── Features
├── Architecture
├── ML Pipeline
├── Hybrid Scoring
├── Resume Intelligence
├── Semantic Search
├── Skill Gap Analysis
├── Tech Stack
├── Project Structure
├── Installation
├── Environment Variables
├── Database Setup
├── Seed Dataset
├── Running Locally
├── Testing
├── API Documentation
├── Deployment
├── Limitations
└── Future Work
```

---

## 1. Overview

**JobTrail-AI** is an explainable career discovery and recommendation platform designed for computer science students, engineering graduates, and early-career software developers. Rather than functioning as a black-box job portal or generic keyword search engine, JobTrail-AI combines dense semantic vector embeddings with an explainable multi-factor scoring architecture to recommend jobs and internships while transparently displaying **why** each match was made and **what skills must be bridged**.

---

## 2. Problem

Job recommendation systems typically suffer from three critical shortcomings:
1. **Keyword Brittleness**: Basic string-matching fails to recognize that "PyTorch" implies deep learning proficiency, or that a "Data Engineer" profile has strong overlap with a "Backend Python" role.
2. **Black-Box Opacity**: Modern algorithmic job boards display arbitrary match badges (e.g. "92% Match") without justification, leaving applicants unable to evaluate fit or understand rejection factors.
3. **No Actionable Career Feedback**: Candidates receiving low match ratings are given no diagnostic insight into which competencies are missing or how to become eligible for their target roles.

---

## 3. Solution

JobTrail-AI addresses these challenges through a deterministic, explainable career matching engine:
- **Dense Contextual Modeling**: Textual candidate profiles are mapped into 384-dimensional semantic vector spaces using `all-MiniLM-L6-v2`.
- **4-Dimensional Hybrid Scoring**: Every recommendation is computed from four transparent factors:
  - **50% Semantic Proximity**
  - **25% Skill Compatibility**
  - **15% Eligibility & Degree Criteria**
  - **10% Candidate Workplace Preferences**
- **Actionable Skill Gap Diagnostics**: Every opportunity presents an itemized breakdown of matching skills vs. missing skills, complete with a prioritized skill bridge roadmap.
- **Evidence-Based Explanations**: Human-interpretable justifications generated directly from the underlying vector distances and attribute checks.

---

## 4. Features

### For Candidates
- **Resume Intelligence**: Upload PDF resumes parsed via PyMuPDF to automatically detect contact information, education, degree, graduation year, experience, and 107+ canonical skills.
- **Explainable Match Breakdown**: Deep-dive compatibility views displaying exact percentage breakdowns across Semantic, Skill, Eligibility, and Preference axes.
- **Targeted Skill Gap Roadmaps**: Clear lists of missing competencies with calculated match score impact if acquired.
- **Natural Language Semantic Search**: Search opportunities using descriptive queries such as *"machine learning internship for python student with no experience"* alongside traditional keyword and faceted filters.
- **Application Pipeline Tracker**: Real-time status progression (`Applied` &rarr; `Interview` &rarr; `Selected` &rarr; `Rejected`) with notes.
- **Opportunity Bookmarks**: Save positions to review and apply at your convenience.

### For Recruiters
- **Structured Job Creator**: Post opportunities with required skills, education thresholds, experience levels, and remote flexibility.
- **ML Candidate Pool Ranking**: Ranks all candidate profiles against the job description using the identical explainable hybrid algorithm.

---

## 5. Architecture

```mermaid
graph TD
    Client["React 19 + TypeScript SPA<br/>(Tailwind CSS, Vite, Lucide)"]
    FastAPI["FastAPI REST Server<br/>(Uvicorn, Pydantic v2, CORS, JWT)"]
    
    subgraph CoreServices ["Application & Domain Services"]
        AuthSvc["Auth & Security (bcrypt, JWT)"]
        ProfileSvc["Profile & Skills Service"]
        JobSvc["Job & Application Service"]
        RecSvc["Recommendation Service"]
        ResumeSvc["Resume Intelligence Service"]
    end

    subgraph MLCore ["Machine Learning & Intelligence"]
        PyMuPDF["PyMuPDF Parser"]
        Taxonomy["Normalized Skill Taxonomy (107+ skills)"]
        STModel["Sentence-Transformers (all-MiniLM-L6-v2)"]
        MatchingEngine["Explainable Hybrid Matching Engine"]
        SkillGapEngine["Skill Gap Analysis Engine"]
    end

    subgraph DataStore ["Database & Storage"]
        DB[(SQLite / PostgreSQL via SQLAlchemy)]
        EmbeddingsTable[(Cached Job Embeddings)]
        UploadsDir[/"Uploads Directory (PDF Storage)"/]
    end

    Client -->|HTTP / JSON / JWT| FastAPI
    FastAPI --> AuthSvc
    FastAPI --> ProfileSvc
    FastAPI --> JobSvc
    FastAPI --> RecSvc
    FastAPI --> ResumeSvc

    ResumeSvc --> PyMuPDF
    ResumeSvc --> Taxonomy
    ResumeSvc --> UploadsDir

    RecSvc --> MatchingEngine
    RecSvc --> SkillGapEngine
    MatchingEngine --> STModel
    MatchingEngine --> Taxonomy

    AuthSvc --> DB
    ProfileSvc --> DB
    JobSvc --> DB
    RecSvc --> DB
    RecSvc --> EmbeddingsTable
```

---

## 6. ML Pipeline

The technical pipeline follows 14 deterministic stages:

```text
Resume / Candidate Profile
          ↓
Information Extraction
          ↓
Skill Normalization
          ↓
Candidate Representation
          ↓
Sentence Transformer
          ↓
Semantic Embedding
          ↓
Cosine Similarity
          ↓
Skill Compatibility
          ↓
Eligibility
          ↓
Preferences
          ↓
Hybrid Match Score
          ↓
Ranking
          ↓
Explainable Recommendation
          ↓
Skill Gap Analysis
```

1. **Information Extraction**: PyMuPDF extracts raw structural text flow from uploaded PDF resumes without OCR overhead.
2. **Skill Normalization**: Regex boundary matching identifies skills against a 107-item taxonomy with synonym expansion (e.g. `k8s` &rarr; `Kubernetes`).
3. **Candidate Representation**: Synthesizes a structured profile narrative: headline, skills, education, degree, experience, and interests.
4. **Sentence Transformer Encoding**: Computes dense 384-dimensional vector embeddings using pretrained `all-MiniLM-L6-v2`.
5. **Cosine Similarity**: Measures angular distance between candidate vectors and cached job vectors:
   $$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
6. **Multi-Factor Aggregation**: Combines semantic score with skill, eligibility, and preference checks.
7. **Ranking & Explanation Generation**: Sorts opportunities descending by hybrid score and compiles verified evidence statements.

---

## 7. Hybrid Scoring

The final compatibility score is computed via the following formula:

$$\text{Overall Match Score} = 0.50 \times S_{\text{semantic}} + 0.25 \times S_{\text{skill}} + 0.15 \times S_{\text{eligibility}} + 0.10 \times S_{\text{preference}}$$

### Visual Representation of Match Breakdown

```text
94%
Overall Match

Semantic Match
██████████████████░░ 92%

Skill Match
███████████████████░ 96%

Eligibility
████████████████████ 100%

Preference
████████████████░░░░ 80%

MATCHING SKILLS
✓ Python
✓ Machine Learning
✓ Pandas
✓ SQL

SKILL GAP
○ Docker
○ AWS

WHY THIS JOB?
• Strong technical skill overlap.
• Education requirement is satisfied.
• Your profile has high semantic similarity.
• The job matches your remote preference.
```

- **Semantic Match (50%)**: Captures deep conceptual alignment between profile experience and job responsibilities.
- **Skill Match (25%)**: Proportional weighted overlap of candidate technical skills against required core skills:
  $$S_{\text{skill}} = \frac{\sum_{s \in \text{Matched}} w_s}{\sum_{s \in \text{Required}} w_s}$$
- **Eligibility (15%)**: Evaluates degree level hierarchy (B.Tech, Bachelor's, Master's, Ph.D.) and minimum experience requirements. Missing data defaults to a neutral 50% baseline.
- **Preferences (10%)**: Compares workplace flexibility (Remote/Hybrid/Onsite), location alignment, and job category interests. Missing preferences default to neutral 50%.

---

## 8. Resume Intelligence

PyMuPDF (`fitz`) parses uploaded PDF resumes to extract structured entities:
- **Contact Details**: Phone numbers, emails, and links.
- **Education & Degree**: Degree types (B.Tech, B.S., M.S., Ph.D.), universities, and graduation years.
- **Technical Skills**: Token and phrase-boundary extraction matching 107+ canonical skills, preventing substring false positives (e.g. `Go` vs. `Google`).
- **Profile Completeness**: Evaluates 6 criteria (headline, location, degree, skills &ge; 3, experience, resume text) to compute an audit score (0–100%).

---

## 9. Semantic Search

JobTrail-AI implements a hybrid search mechanism:
- **Natural Language Search**: Queries like *"machine learning internship for python student with no experience"* are encoded via `all-MiniLM-L6-v2` and compared against cached job vectors.
- **Keyword Boosting**: Exact title and skill matches apply additive boosts to ensure keyword precision without losing semantic breadth.
- **Faceted Filtering**: Filter by category, remote flexibility, experience level, and geographic location.

---

## 10. Skill Gap Analysis

- **Per-Job Diagnostics**: For any selected opportunity, identifies exact missing skills and highlights required competencies.
- **Portfolio-Level Readiness**: Aggregates missing skills across all top-ranked recommendations, identifying high-leverage technologies that will unlock the greatest number of matching roles.
- **Career Strategy Insights**: Generates prescriptive steps to prepare candidates for interview loops.

---

## 11. Tech Stack

- **Backend Framework**: Python 3.12, FastAPI, Uvicorn
- **ORM & Database**: SQLAlchemy 2.0, SQLite (PostgreSQL compatible)
- **Machine Learning**: `sentence-transformers`, `torch`, `numpy`, `all-MiniLM-L6-v2`
- **Document Intelligence**: PyMuPDF (`fitz`)
- **Frontend Framework**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS, Lucide Icons
- **State Management**: React Query (`@tanstack/react-query`), AuthContext
- **Testing**: Pytest, FastAPI TestClient, HTTPX
- **Containerization**: Docker, Docker Compose, Nginx

---

## 12. Project Structure

```text
JobTrail-AI/
├── backend/
│   ├── app/
│   │   ├── api/             # 9 REST routers (auth, profile, resume, jobs, recommendations, search, skill_gap, applications, recruiter)
│   │   ├── core/            # Config, security, JWT helpers
│   │   ├── db/              # SQLAlchemy session & base setup
│   │   ├── ml/              # EmbeddingService, MatchingEngine, SkillExtractor, SkillGapEngine
│   │   ├── models/          # SQLAlchemy ORM models (User, Job, Skill, Application, SavedJob, Embedding)
│   │   ├── resume/          # PyMuPDF extractor, entity parser & profile calculator
│   │   ├── schemas/         # Pydantic v2 validation models
│   │   ├── seed/            # Idempotent database seeder & embedding generator
│   │   ├── services/        # Domain business logic services
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # 31 automated tests
│   ├── Dockerfile           # Backend container image
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (Navbar, Footer, JobCard, MatchBreakdownCard, DemoGuideBar, SkillGapCard)
│   │   ├── context/         # AuthContext with token persistence
│   │   ├── pages/           # 16 pages (Landing, HowItWorks, Dashboard, Jobs, JobDetail, MatchAnalysis, Resume, Recruiter, etc.)
│   │   ├── services/        # Type-safe API client with sanitized error handling
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # React Router setup & protected routes
│   │   └── main.tsx         # Root React entrypoint
│   ├── Dockerfile           # Multi-stage production build
│   ├── nginx.conf           # Nginx reverse proxy configuration
│   ├── package.json         # Frontend dependencies
│   └── vite.config.ts       # Vite bundler configuration
│
├── data/
│   ├── jobs.json            # 305 structured synthetic prototype job records
│   ├── skills.json          # Canonical technical skill taxonomy with aliases
│   └── sample_resume.pdf    # Synthetic candidate resume fixture (Satvik Sharma)
│
├── docs/
│   ├── architecture.md      # Detailed system architecture & Mermaid diagrams
│   ├── api.md               # Complete REST API reference
│   ├── ml-pipeline.md       # Machine learning methodology & mathematical scoring
│   └── testing.md           # Automated testing documentation & verification commands
│
├── uploads/                 # Uploaded PDF resumes directory (.gitkeep)
├── .env.example             # Example environment variables
├── docker-compose.yml       # Docker Compose multi-container setup
└── README.md                # Project documentation
```

---

## 13. Installation

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

```bash
git clone https://github.com/Satvik2Sharma/JobTrail-AI.git
cd JobTrail-AI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## 14. Environment Variables

Create `.env` in the project root:

```ini
PROJECT_NAME="JobTrail-AI"
SECRET_KEY="jobtrail-ai-super-secret-key-change-in-production-2026"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL="sqlite:///./jobtrail.db"
EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR="./uploads"
```

---

## 15. Database Setup

The database schema is initialized and seeded automatically using the idempotent pipeline script:

```bash
source .venv/bin/activate
PYTHONPATH=backend python -m app.seed.seed_database
```

This pipeline:
1. Creates all SQLite tables (`users`, `profiles`, `skills`, `jobs`, `job_skills`, `job_embeddings`, `saved_jobs`, `applications`).
2. Populates 107 canonical skills with aliases.
3. Loads 305 structured prototype jobs.
4. Computes and caches 305 `all-MiniLM-L6-v2` dense vector embeddings.
5. Creates pre-configured demo candidate and recruiter accounts.

---

## 16. Seed Dataset

- **Jobs (`data/jobs.json`)**: 305 prototype roles across AI/ML, Data Science, Backend, Frontend, Cloud/DevOps, and Cybersecurity.
- **Skills (`data/skills.json`)**: 107 canonical skills with aliases and categorizations.
- **Sample Resume (`data/sample_resume.pdf`)**: Synthetic PDF resume for Satvik Sharma (B.Tech CS, 10 skills).

---

## 17. Running Locally

Open two terminal windows:

### Terminal 1 — Backend API
```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API available at `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`).*

### Terminal 2 — Frontend Application
```bash
cd frontend
npm run dev
```
*Web application available at `http://localhost:5173`.*

---

## 18. Testing

JobTrail-AI features a comprehensive 31-test automated suite:

```bash
PYTHONPATH=backend .venv/bin/pytest backend/tests/ -v
```

### Verified Test Results (31 passed, 100%)
- **`test_ml_matching.py`** (11 tests): Skill extraction, normalization, cosine similarity, eligibility hierarchy, preference alignment, and hybrid formula.
- **`test_recommendation_ranking.py`** (2 tests): Validates synthetic Candidate A preference ranking (ML Intern > Backend Dev > Cloud Architect) and multi-candidate differentials.
- **`test_resume_service.py`** (4 tests): PyMuPDF extraction, entity parsing, completeness scoring, and safe file handling.
- **`test_unknown_data.py`** (2 tests): Confirms neutral 50% baseline for missing candidate attributes without claiming 100%.
- **`test_api_endpoints.py`** (12 tests): Auth, profile CRUD, resume upload, jobs, recommendations, skill gap, saved jobs, application status modifications, unauthorized 403 prevention, semantic search, and recruiter ranking.

---

## 19. API Documentation

Interactive OpenAPI / Swagger documentation is available at `http://localhost:8000/docs`.

Key endpoints include:
- `POST /api/auth/register` — Register new candidate or recruiter.
- `POST /api/auth/login` — Authenticate and receive JWT Bearer token.
- `GET /api/profile` / `PUT /api/profile` — Candidate profile management.
- `POST /api/resume/upload` — PyMuPDF PDF parsing and skill extraction.
- `GET /api/jobs` — Faceted job search and listing.
- `GET /api/recommendations` — Personalized top-ranked opportunities with hybrid scoring.
- `GET /api/jobs/{id}/match` — Explainable 4D match breakdown and evidence reasons.
- `GET /api/skill-gap` — Target role or portfolio-level skill gap roadmap.
- `GET /api/search` — Natural language semantic vector search.
- `POST /api/jobs/{id}/apply` — 1-click application submission.
- `GET /api/recruiter/jobs/{id}/candidates` — Recruiter candidate pool ranking.

---

## 20. Deployment

To run the entire production-ready stack in Docker:

```bash
docker compose up --build
```

- **Frontend (Nginx)**: `http://localhost:3000`
- **Backend (FastAPI)**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

---

## 21. Limitations

1. **OCR Processing**: Scanned or raster image-only PDFs require selectable text; scanned PDFs without a text layer need an external OCR preprocessing step (e.g., Tesseract).
2. **Synthetic Dataset**: The 305 job listings are synthetic prototype records designed for benchmark testing and evaluation, not live scraped employer postings.
3. **In-Memory Vector Search**: Vector cosine similarity is computed directly across SQLite-cached embeddings. While highly performant for hundreds of prototype jobs, scaling beyond 50,000 jobs requires an external vector index (e.g. Qdrant or `pgvector`).

---

## 22. Future Work

- [ ] **Vector Database**: Migrate cached embeddings to Qdrant or PostgreSQL `pgvector`.
- [ ] **Live Job Feed Integrations**: Ingest public jobs via Greenhouse or Lever public APIs.
- [ ] **Deep Learning-to-Rank (LTR)**: Incorporate implicit feedback (clicks, saves, applications) into a reranking model.
- [ ] **Recruiter Talent Analytics**: Cohort analytics, time-to-hire estimation, and talent pool diversity metrics.
- [ ] **Optional LLM Explanation Layer**: Optional natural language summary generation using an open-source local LLM (e.g., Gemma-2B).

---

## Demo Flow

For evaluators and professors, the recommended demonstration path is:

```text
1. Login (1-Click Demo: demo@jobtrail.local)
   ↓
2. Resume Intelligence (inspect PyMuPDF parsing & normalized skills)
   ↓
3. Dashboard (review top-ranked recommendations & profile completeness)
   ↓
4. Top Match (click 1st job to inspect position)
   ↓
5. Match Analysis (view 4D hybrid score breakdown & evidence reasons)
   ↓
6. Skill Gap (review missing skills & readiness impact)
   ↓
7. Semantic Search (try: "machine learning internship for python student")
   ↓
8. Save & Apply (bookmark role and submit 1-click application)
   ↓
9. Application Tracker (track recruitment progression)
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
