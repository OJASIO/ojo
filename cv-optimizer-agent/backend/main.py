from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile

from backend.extractor import extract_text
from backend.language_detector import detect_language
from backend.cv_reviewer import review_cv
from backend.ats_checker import check_ats
from backend.models import CVReviewResponse
from fastapi.responses import FileResponse  

app = FastAPI(title="CV Optimizer Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "running", "service": "CV Optimizer Agent"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "supported_languages": ["en", "de"],
        "supported_formats": ["pdf", "docx"]
    }

@app.get("/app")
def serve_frontend():
    return FileResponse("frontend.html")

@app.post("/review-cv")
async def review_cv_endpoint(file: UploadFile = File(...)):

    # Step 1 — validate file format
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Please upload PDF or DOCX."
        )

    # Step 2 — save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Step 3 — extract text
        cv_text = extract_text(tmp_path)

        if not cv_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this document. "
            "This usually happens when the PDF is a scanned image "
            "or contains redaction boxes covering the text. "
            "Please upload a digitally created PDF or a DOCX file instead."
            )

        # Step 4 — detect language
        lang = detect_language(cv_text)

        # Step 5 — LLM review
        llm_result = review_cv(cv_text, lang)

        # Step 6 — ATS check
        ats_result = check_ats(cv_text)

        # Step 7 — return combined response
        return {
            "filename": file.filename,
            "language": lang,
            "overall_score": llm_result.get("overall_score", 0),
            "tier_1": llm_result.get("tier_1", []),
            "tier_2": llm_result.get("tier_2", []),
            "tier_3": llm_result.get("tier_3", []),
            "summary": llm_result.get("summary", ""),
            "ready_for_counseling": llm_result.get("ready", False),
            "ats_score": ats_result.get("score", 0),
            "ats_issues": ats_result.get("issues", []),
            "recommendation": ats_result.get("recommendation", "")
        }

    finally:
        os.remove(tmp_path)