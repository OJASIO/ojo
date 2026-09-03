import json
import os
import re
from dotenv import load_dotenv
from google import genai
from backend.prompts import get_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)


def anonymise_text(text: str, lang: str, file_path: str = None) -> str:
    """
    Four-layer anonymisation:
    Layer 1 — regex for emails, phones, postal codes, URLs
    Layer 2 — regex for date of birth line
    Layer 3 — font-size based name extraction (PDF)
               or first-line heuristic (DOCX)
    Layer 4 — address regex on header only
    """

    # Layer 1 — pattern matching on full text
    # Email addresses
    text = re.sub(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        '[EMAIL]', text
    )

    # Phone numbers starting with + or 0
    text = re.sub(
        r'(\+\d[\d\s\-\(\)]{7,}\d|0\d[\d\s\-\(\)]{6,}\d)',
        '[PHONE]', text
    )

    # German postal codes
    text = re.sub(
        r'\b\d{5}\b',
        '[PLZ]', text
    )

    # LinkedIn URLs
    text = re.sub(
        r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?',
        '[LINKEDIN REMOVED]', text
    )

    # GitHub project links — remove username keep project name
    text = re.sub(
        r'(https?://)?(www\.)?github\.com/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-_\.]+)',
        r'github.com/[GITHUB USER]/\4', text
    )

    # GitHub profile links — remove entirely
    text = re.sub(
        r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9\-]+/?',
        '[GITHUB REMOVED]', text
    )

    # Personal portfolio and live project websites
    text = re.sub(
        r'(https?://)?(www\.)?[a-zA-Z0-9\-]+\.'
        r'(github\.io|me|dev|portfolio|site|web\.app|streamlit\.app)'
        r'(/[^\s]*)?',
        '[PERSONAL WEBSITE REMOVED]', text
    )

    # Layer 2 — date of birth line on full text
    dob_pattern = (
        r'(Geburtsdatum|Geburtsort|Geboren am|'
        r'Date of Birth|DOB|Birthdate|Birth date)[^\n]*'
    )
    text = re.sub(
        dob_pattern, '[DOB REMOVED]', text, flags=re.IGNORECASE
    )

    # Layer 3 — font-size based name extraction
    names_found = set()

    if file_path and file_path.lower().endswith('.pdf'):
        from backend.extractor import extract_name_from_pdf
        name = extract_name_from_pdf(file_path)
        if name and len(name) > 3:
            names_found.add(name)
            names_found.add(name.upper())
            names_found.add(name.title())
    else:
        # Fallback for DOCX — first non-empty line heuristic
        lines = text.split('\n')
        for line in lines[:5]:
            stripped = line.strip()
            words = stripped.split()
            if (1 <= len(words) <= 4
                    and len(stripped) > 3
                    and not any(c in stripped for c in
                                ['@', '/', '|', ':', 'http'])):
                names_found.add(stripped)
                names_found.add(stripped.upper())
                names_found.add(stripped.title())
                break

    # Remove all name variants from full text
    for name in names_found:
        if len(name) > 3:
            text = text.replace(name, '[PER]')

    # Split into header and body
    section_markers = [
        'BERUFSERFAHRUNG', 'WORK EXPERIENCE', 'EXPERIENCE',
        'PROFESSIONAL EXPERIENCE', 'PRAKTISCHE ERFAHRUNG',
        'AUSBILDUNG', 'EDUCATION', 'KOMPETENZEN', 'SKILLS',
        'TECHNICAL SKILLS', 'KENNTNISSE', 'SCHULISCHE',
        'STUDIUM', 'STUDIENPROJEKTE', 'ACADEMIC PROJECTS',
        'PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFIL',
        'ZERTIFIKATE', 'HOBBYS', 'P R O F I L',
        'S T U D I E N', 'K E N N T N I S S E',
        'P R A K T I S C H E', 'A U S B I L D U N G'
    ]

    personal_sections = [
        'PERSÖNLICHE DATEN', 'PERSONAL DETAILS',
        'PERSONAL INFORMATION', 'KONTAKT', 'CONTACT',
        'ÜBER MICH', 'ABOUT ME'
    ]

    text_upper = text.upper()

    header_end = len(text)
    for marker in section_markers:
        idx = text_upper.find(marker)
        if idx != -1 and idx < header_end:
            header_end = idx

    for marker in personal_sections:
        idx = text_upper.find(marker)
        if idx != -1 and idx < header_end:
            next_section = header_end
            for content_marker in section_markers:
                cidx = text_upper.find(content_marker, idx)
                if cidx != -1 and cidx < next_section:
                    next_section = cidx
            header_end = next_section

    header = text[:header_end]
    body = text[header_end:]

    # Layer 4 — address regex on header only
    header = re.sub(
        r'[A-ZÄÖÜ][a-zäöüß]+(strasse|straße|str\.|weg|gasse|'
        r'allee|platz|ring|damm|ufer)\s*\d+[a-zA-Z]?'
        r'(\s*,\s*Wohnung\s*[\d\.]+)?',
        '[ADDRESS REMOVED]', header,
        flags=re.IGNORECASE
    )

    return header + body


def review_cv(cv_text: str, lang: str,
              file_path: str = None) -> dict:
    """
    Anonymise CV text then send to Gemini for tiered review.
    """
    clean_text = anonymise_text(cv_text, lang, file_path)

    prompt = get_prompt(lang).format(cv_text=clean_text)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"JSON parse failed. Raw response:\n{raw[:300]}")
        return {
            "overall_score": 0,
            "tier_1": [],
            "tier_2": [],
            "tier_3": [],
            "summary": "Analysis could not be completed. Please try again.",
            "ready": False,
        }