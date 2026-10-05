# JobTrail-AI — Machine Learning & Recommendation Methodology

## 1. Core Principles

JobTrail-AI implements a deterministic, explainable, multi-factor recommendation pipeline designed specifically for students, fresh graduates, and career changers.

> **Methodological Disclaimer**: JobTrail-AI uses a pretrained Sentence Transformer (`sentence-transformers/all-MiniLM-L6-v2`) for semantic representation and a custom explainable hybrid recommendation/ranking pipeline. It does not claim to train a transformer from scratch, nor does it fabricate scores via stochastic large language models.

---

## 2. ML Architecture & Pipeline

```text
                  CANDIDATE INPUTS
    [Skills, Degree, Experience, Preferences, Resume]
                          │
                          ▼
            [Candidate Text Representation]
                          │
                          ▼
             [SentenceTransformer MiniLM]
                          │
                          ▼
              [384-d Candidate Vector]
                          │
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
[Job Vector Cache]                  [Job Requirements]
(Precomputed 305 Embeddings)       (Skills, Degree, Experience)
       │                                     │
       ▼                                     ▼
[Cosine Similarity]                [Rule-based Evaluators]
(Raw Cosine -> Normalized)         (Skill, Eligibility, Pref)
       │                                     │
       └──────────────────┬──────────────────┘
                          │
                          ▼
             [Explainable Hybrid Scorer]
        0.50 Semantic + 0.25 Skill + 0.15 Eligibility + 0.10 Preference
                          │
                          ▼
         [Ranked Recommendations + Evidence Reasons]
```

---

## 3. Candidate & Job Text Representations

### Candidate Profile Text Formulation
To allow Sentence-Transformers to capture semantic context effectively, structured profile attributes are assembled into a deterministic textual representation:
```python
parts = ["Candidate Profile:"]
if degree:
    parts.append(f"Education: {degree} in {field}.")
if experience_years > 0:
    parts.append(f"Experience: {experience_years:.1f} years in tech.")
else:
    parts.append("Experience: Student / Entry-level.")
if skills:
    parts.append(f"Skills: {', '.join(skills)}.")
if interests:
    parts.append(f"Interests & Career Focus: {interests}.")
if resume_summary:
    parts.append(f"Background: {resume_summary[:300]}.")
```

### Job Description Text Formulation
Jobs are embedded during database seeding and upon creation:
```python
parts = [
    f"Job Title: {title}.",
    f"Category: {category}.",
    f"Experience: {experience_level}.",
    f"Required Skills: {', '.join(skills)}.",
    f"Description: {description[:350]}."
]
if requirements:
    parts.append(f"Requirements: {requirements[:200]}.")
```

---

## 4. Scoring Dimensions & Exact Formula

The scoring weights are centrally managed in `app/core/config.py`:

```python
SEMANTIC_WEIGHT    = 0.50
SKILL_WEIGHT       = 0.25
ELIGIBILITY_WEIGHT = 0.15
PREFERENCE_WEIGHT  = 0.10
```

$$\text{Overall Match Score} = 0.50 \times S_{\text{semantic}} + 0.25 \times S_{\text{skill}} + 0.15 \times S_{\text{eligibility}} + 0.10 \times S_{\text{preference}}$$

### A. Semantic Similarity ($S_{\text{semantic}}$)
- Vector dimension: 384 (MiniLM-L6-v2, normalized embeddings).
- Metric: Cosine similarity $\frac{u \cdot v}{\|u\|_2 \|v\|_2}$.
- Normalization: Raw cosine scores for technical role descriptions typically cluster between $[0.20, 0.90]$. The engine applies a calibrated linear projection:
  $$S_{\text{semantic}} = \text{clamp}\left(\frac{\text{raw} - 0.20}{0.70}, 0.0, 1.0\right)$$

### B. Explicit Skill Match ($S_{\text{skill}}$)
- Every required job skill is weighted by importance:
  $$\text{weight} = \text{importance} \times (1.5 \text{ if required else } 1.0)$$
- Candidate skills are matched against job requirements using the normalized skill taxonomy (e.g. `py` $\rightarrow$ `Python`, `sklearn` $\rightarrow$ `Scikit-learn`).
- $$S_{\text{skill}} = \frac{\sum_{\text{matched}} \text{weight}_i}{\sum_{\text{all job skills}} \text{weight}_i}$$

### C. Eligibility Match ($S_{\text{eligibility}}$)
- **Education (60% weight)**: Checks degree level (Undergraduate, Bachelor's, Master's) and STEM/CS field relevance. Unspecified education defaults to neutral 0.60, matching degree and field earns 1.0.
- **Experience (40% weight)**: Compares candidate years of experience against stated minimums (`0-1 years`, `1-2 years`, `3+ years`).
- Transparently preserves unknown information without hallucinating 100%.

### D. Preference Match ($S_{\text{preference}}$)
- **Workplace Mode (Remote / Hybrid / On-site)**: Remote candidate matching remote role earns 1.0; on-site mismatch receives 0.30; hybrid is flexible (0.80–0.90).
- **Location Alignment**: Compares preferred city with job location (remote jobs automatically satisfy location preferences).
- **Career Domain Alignment**: Checks candidate's domain interest tags against job category.

---

## 5. Explainable Justification Generation

Rather than emitting an opaque percentage, the engine maps computed component metrics to human-readable factual rationales:
- **Skill Justification**: "Strong overlap with technical skills (4 matched)." or "Moderate skill overlap with foundational competencies."
- **Eligibility Justification**: "Your degree and field of study fully satisfy educational requirements."
- **Semantic Justification**: "Your profile has high contextual and semantic similarity to this role."
- **Workplace Justification**: "Remote flexibility matches your remote work preference."

---

## 6. Semantic Search Mechanism

Natural-language job search (`GET /api/search?q=...`) operates as follows:
1. Candidate query text is vectorized on-the-fly via `embedding_service.encode_text(q)`.
2. Query vector is compared with all pre-cached job embeddings via vectorized dot products.
3. Keyword boosts (up to $+0.15$) are added for direct substring occurrences in the title or company.
4. Results are sorted and returned in sub-100ms response times without external search appliances.
