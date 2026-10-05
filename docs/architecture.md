# JobTrail-AI — System Architecture

## 1. System Overview

**JobTrail-AI** is an AI-powered job and internship recommendation platform featuring explainable career matching and skill-gap analysis. The system is designed with a modern decoupled client-server architecture:

- **Frontend**: Single Page Application built with React 19, Vite, TypeScript, Tailwind CSS, Lucide icons, and Recharts.
- **Backend API**: High-performance asynchronous REST API powered by FastAPI, Pydantic v2, and SQLAlchemy.
- **Machine Learning Core**: Sentence-Transformers (`sentence-transformers/all-MiniLM-L6-v2`), Scikit-Learn cosine similarity metrics, and an Explainable Multi-Factor Matching Engine.
- **Resume Intelligence Engine**: Modular PDF parsing pipeline utilizing PyMuPDF (`pymupdf`) for non-destructive layout analysis and deterministic taxonomy-backed skill extraction.
- **Persistence Layer**: SQLite database (migratable to PostgreSQL via SQLAlchemy ORM) with cached vector embeddings stored as serialized tensors.

---

## 2. High-Level System Architecture

```mermaid
graph TD
    Client["React + TypeScript SPA<br/>(Tailwind CSS, Vite, Lucide)"]
    FastAPI["FastAPI REST Server<br/>(Uvicorn, Pydantic v2, CORS, JWT)"]
    
    subgraph CoreServices ["Application & Domain Services"]
        AuthSvc["Auth & Security<br/>(bcrypt, JWT HS256)"]
        ProfileSvc["Profile & Skills Service"]
        JobSvc["Job & Application Service"]
        RecSvc["Recommendation Service"]
        ResumeSvc["Resume Intelligence Service"]
    end

    subgraph MLCore ["Machine Learning & Intelligence"]
        PyMuPDF["PyMuPDF Parser"]
        Taxonomy["Normalized Skill Taxonomy<br/>(107+ canonical skills)"]
        STModel["Sentence-Transformers<br/>(all-MiniLM-L6-v2 Singleton)"]
        MatchingEngine["Explainable Hybrid Matching Engine<br/>(Semantic, Skill, Eligibility, Preference)"]
        SkillGapEngine["Skill Gap Analysis Engine"]
    end

    subgraph DataStore ["Database & Storage"]
        DB[(SQLite / PostgreSQL<br/>SQLAlchemy ORM)]
        EmbeddingsTable[(Cached Job Embeddings<br/>384-d Float32 Arrays)]
        UploadsDir[/"Uploads Directory<br/>Safe PDF File Storage"/]
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

## 3. Resume Intelligence Pipeline

```mermaid
graph LR
    PDF[Candidate Resume PDF] --> Parser[PyMuPDF Parser]
    Parser --> RawText[Extracted Raw Text]
    RawText --> EntityExtract[Regex & Heuristic Entity Extraction<br/>Name, Email, Phone, Degree, Experience]
    RawText --> SkillExtractor[Taxonomy Word-Boundary Matcher]
    SkillExtractor --> CanonicalSkills[Normalized Canonical Skills]
    EntityExtract --> CandProfile[Candidate Structured Profile]
    CanonicalSkills --> CandProfile
    CandProfile --> CandRepr[Deterministic Text Representation]
    CandRepr --> ST[Sentence-Transformers all-MiniLM-L6-v2]
    ST --> CandVec[384-dimensional Normalized Vector]
    CandVec --> HybridRec[Hybrid Matching Engine]
```

---

## 4. Explainable Matching & Ranking Flow

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Candidate
    participant UI as Frontend App
    participant API as FastAPI Router
    participant Engine as Explainable Matching Engine
    participant Model as MiniLM Transformer
    participant DB as SQLite Database

    Candidate->>UI: Navigates to Dashboard / Recommendations
    UI->>API: GET /api/recommendations
    API->>DB: Fetch Candidate Profile & Active User Skills
    API->>Model: Compute Candidate Embedding vector
    API->>DB: Query 305 Jobs & Pre-computed Job Vectors
    loop For Each Job
        API->>Engine: match_candidate_to_job()
        Engine->>Engine: Cosine Similarity (Semantic 50%)
        Engine->>Engine: Weighted Skill Overlap (Skill 25%)
        Engine->>Engine: Degree & Experience Rules (Eligibility 15%)
        Engine->>Engine: Workplace Preference Alignment (Preference 10%)
        Engine-->>API: Return Overall Score & Concrete Justifications
    end
    API->>API: Sort Descending by Overall Match Score
    API-->>UI: Return Ranked Recommendations + Score Breakdown
    UI-->>Candidate: Render Top Job Cards with Match Badges & Details
```

---

## 5. Security Architecture

1. **Password Hashing**: Industry-standard `bcrypt` algorithm with automated salting.
2. **Stateless JWT Tokens**: Cryptographic `HS256` signed tokens holding candidate ID and role, valid for 24 hours.
3. **Role-Based Access Control (RBAC)**: Enforced via FastAPI dependency injection (`get_current_user`, `get_current_recruiter`).
4. **File Safety**: Uploaded files validated for MIME type (`application/pdf`), 10MB file size ceiling, and path traversal sanitization with UUID prefixes.
5. **CORS Policy**: Configurable origin whitelisting via environment variables.
