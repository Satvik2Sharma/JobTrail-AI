# JobTrail-AI — Automated Testing Suite

## 1. Test Suite Architecture

JobTrail-AI incorporates comprehensive automated unit and integration tests spanning machine learning mathematics, recommendation correctness, PDF resume intelligence extraction, and end-to-end REST API endpoints.

```text
backend/tests/
├── conftest.py                      # Isolated SQLite DB fixture, seeded test roles & tokens
├── test_ml_matching.py              # ML formula, weights, similarity & rule evaluators (11 tests)
├── test_recommendation_ranking.py   # Multi-candidate ranking differential & correctness (2 tests)
├── test_resume_service.py           # PyMuPDF text & attribute extraction, file validation (4 tests)
├── test_unknown_data.py             # Unknown/incomplete profile handling & neutral baseline (2 tests)
└── test_api_endpoints.py            # End-to-end REST API & security integration tests (12 tests)
```

**Total Automated Tests**: **31 Passed (100% Passing)**

---

## 2. Test Modules Description

### A. `test_ml_matching.py` (11 Tests)
- `test_skill_extractor_normalization`: Verifies canonical mapping for aliases (`py` $\rightarrow$ `Python`, `sklearn` $\rightarrow$ `Scikit-learn`, `k8s` $\rightarrow$ `Kubernetes`, etc.).
- `test_skill_extractor_from_text`: Validates regex word-boundary skill extraction without false substring positives.
- `test_skill_match_full_overlap`: Asserts 100% score when candidate matches all required skills.
- `test_skill_match_partial_overlap`: Verifies exact proportional scoring (e.g. 50% for 2 of 4 skills).
- `test_skill_match_zero_overlap`: Confirms 0% score and complete missing skills identification.
- `test_eligibility_match_btech_cs_entry_level`: Validates degree and entry-level requirement satisfaction.
- `test_eligibility_match_experience_gap`: Checks penalty application when entry-level candidate applies to 3+ years senior role.
- `test_preference_match_remote_alignment`: Asserts 100% score when remote preference matches remote role.
- `test_preference_match_mismatch`: Validates score degradation on on-site vs. remote mismatch.
- `test_cosine_similarity_properties`: Confirms mathematical properties (1.0 for identical vectors, 0.0 for orthogonal vectors).
- `test_hybrid_matching_score_formula`: Checks 4-factor weighted score calculation within $[0, 100]$.

### B. `test_recommendation_ranking.py` (2 Tests)
- `test_recommendation_ranking_candidate_a_synthetic_fixture`: Implements the Section 39 synthetic candidate benchmark:
  - **Candidate A Profile**: B.Tech Computer Science, Skills: [Python, Machine Learning, Pandas, NumPy, SQL, FastAPI, React, Git], 0–1 years experience.
  - **Verification**: Asserts strictly that:
    $$\text{Score}(\text{Machine Learning Intern}) > \text{Score}(\text{Junior Backend Dev}) > \text{Score}(\text{Senior Cloud Architect})$$
    and that the ML Intern is ranked #1.
- `test_multiple_candidates_ranking_differential`: Proves differential ranking across distinct profiles:
  - **Candidate B (Frontend)**: React & TypeScript specialist.
  - **Candidate C (DevOps)**: Kubernetes, AWS, CI/CD specialist.
  - Asserts Candidate C ranks Senior Cloud Architect above ML Intern, validating recommendation personalization.

### C. `test_resume_service.py` (4 Tests)
- `test_resume_service_extract_text_from_sample`: Tests PyMuPDF text extraction from synthetic PDF fixture.
- `test_resume_service_intelligence_parsing`: Validates contact info, degree, graduation year, and skill extraction from resume text.
- `test_resume_service_completeness_calculation`: Verifies deterministic completeness calculation based on actual present fields.
- `test_resume_service_file_validation`: Enforces rejection of non-PDFs and files exceeding the 10MB upload ceiling.

### D. `test_api_endpoints.py` (11 Tests)
- `test_auth_registration_and_login`: Tests registration, login, JWT issuance, and `/api/auth/me`.
- `test_auth_login_invalid_password`: Verifies 401 Unauthorized for bad credentials.
- `test_candidate_profile_operations`: Tests GET profile, PUT profile, add skill, and remove skill.
- `test_resume_upload_and_extraction`: Tests multipart file upload and GET `/api/resume`.
- `test_jobs_list_and_filters`: Validates job pagination and remote/category filtering.
- `test_recommendations_and_explainable_match`: Validates `/api/recommendations` and `/api/jobs/{id}/match` response contracts.
- `test_skill_gap_analysis`: Validates aggregate and per-job skill gap endpoints.
- `test_saved_jobs_lifecycle`: Tests bookmarking and removing jobs.
- `test_application_lifecycle`: Tests job application submission, listing, and status updates.
- `test_semantic_search_endpoint`: Tests natural-language semantic query execution.
- `test_recruiter_endpoints`: Tests recruiter job creation and candidate ranking.

---

## 3. Running the Test Suite

Execute the entire test suite from the repository root:

```bash
# Run all tests with verbose output
PYTHONPATH=backend .venv/bin/pytest backend/tests/ -v

# Run a specific test module
PYTHONPATH=backend .venv/bin/pytest backend/tests/test_recommendation_ranking.py -v

# Run with test duration profiling
PYTHONPATH=backend .venv/bin/pytest backend/tests/ --durations=5
```
