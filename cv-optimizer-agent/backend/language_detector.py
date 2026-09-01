from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"
    try:
        lang = detect(text[:500])
        return "de" if lang == "de" else "en"
    except LangDetectException:
        return "unknown"

def get_language_label(lang_code: str) -> str:
    return {"de": "German (DE)", "en": "English (EN)","unknown": "No text detected"}.get(lang_code, "Unknown")