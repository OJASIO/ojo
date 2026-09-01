# CV Optimizer Agent

AI-powered CV review system for SRH Career Service.
Supports English (EN-GB) and German (DE-DE) CVs.

## Quick Start

```bash
# 1. Copy env file and add your Gemini API key
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start backend
uvicorn backend.main:app --reload

# 4. Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Project Structure

```
cv-optimizer-agent/
├── backend/
│   ├── main.py              ← FastAPI app and /review-cv endpoint
│   ├── config.py            ← Settings loaded from .env
│   ├── models.py            ← Pydantic request/response models
│   ├── extractor.py         ← PDF and DOCX text extraction
│   ├── language_detector.py ← EN / DE detection with langdetect
│   ├── grammar_checker.py   ← LanguageTool rule-based baseline
│   ├── cv_reviewer.py       ← Gemini LLM tiered review
│   ├── ats_checker.py       ← ATS compatibility scoring
│   └── prompts.py           ← All LLM prompt templates
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── UploadZone.jsx
│           ├── ScoreCard.jsx
│           ├── FeedbackSection.jsx
│           └── TierCard.jsx
├── data/
│   └── sample_cvs/          ← Place real CVs here (gitignored)
├── evaluation/
│   ├── test_runner.py       ← Compares agent output vs human baseline
│   └── ground_truth.json    ← Human counselor annotations
├── tests/
│   ├── test_extractor.py
│   ├── test_language_detector.py
│   └── test_cv_reviewer.py
├── requirements.txt
└── .env.example
```

## Implementation Order

1. `extractor.py`         — Foundation, implement first
2. `language_detector.py` — Simple, 5 lines
3. `grammar_checker.py`   — LanguageTool baseline
4. `prompts.py`           — Already complete
5. `cv_reviewer.py`       — LLM call + JSON parsing
6. `ats_checker.py`       — ATS heuristics
7. `main.py`              — Wire everything together
8. `frontend/`            — React UI (already built as demo)
9. `evaluation/`          — Run after implementation complete

## API

```
POST /review-cv
  Body: multipart/form-data with file (PDF or DOCX)
  Returns: CVReviewResponse JSON

GET  /health
  Returns: status and supported languages
```

## Research Questions (Thesis)

- RQ1: Does LLM review catch more issues than LanguageTool baseline?
  → Compare cv_reviewer.py output vs grammar_checker.py output on same CVs

- RQ2: How well does the agent match human counselor feedback?
  → Run evaluation/test_runner.py and check precision/recall

- RQ3: How do students perceive the feedback?
  → User study with 15 students using the frontend
