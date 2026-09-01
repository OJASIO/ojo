import re
from typing import Dict, List


def check_ats(cv_text: str) -> Dict:
    """
    Run all ATS checks and return a score and list of issues.
    Score starts at 100 and deductions are made per issue found.
    """
    issues = []

    issues += _check_date_consistency(cv_text)
    issues += _check_email_present(cv_text)
    issues += _check_phone_present(cv_text)
    issues += _check_section_headings(cv_text)
    issues += _check_special_characters(cv_text)

    score = _calculate_score(issues)

    return {
        "score": score,
        "issues": issues,
        "recommendation": _get_recommendation(score)
    }


def _check_date_consistency(cv_text: str) -> List[Dict]:
    """Detect mixed date formats in the same CV."""
    issues = []

    formats_found = []
    if re.search(r'\d{2}/\d{4}', cv_text):
        formats_found.append("MM/YYYY")
    if re.search(r'\d{2}\.\d{4}', cv_text):
        formats_found.append("MM.YYYY")
    if re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', cv_text):
        formats_found.append("Mon YYYY")
    if re.search(r'(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}', cv_text):
        formats_found.append("Monat JJJJ")

    if len(formats_found) > 1:
        issues.append({
            "issue": f"Inconsistent date formats found: {', '.join(formats_found)}",
            "severity": "high"
        })

    return issues


def _check_email_present(cv_text: str) -> List[Dict]:
    """Check that a valid email address exists."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if not re.search(pattern, cv_text):
        return [{"issue": "No email address found", "severity": "high"}]
    return []


def _check_phone_present(cv_text: str) -> List[Dict]:
    """Check that a phone number exists."""
    pattern = r'(\+?\d[\d\s\-\(\)]{7,}\d)'
    if not re.search(pattern, cv_text):
        return [{"issue": "No phone number found", "severity": "high"}]
    return []


def _check_section_headings(cv_text: str) -> List[Dict]:
    """Check that standard section headings are present."""
    issues = []
    text_upper = cv_text.upper()

    required = {
        "education": ["EDUCATION", "AUSBILDUNG", "STUDIUM", "SCHULISCHE"],
        "experience": ["EXPERIENCE", "BERUFSERFAHRUNG", "ERFAHRUNG"],
        "skills": ["SKILLS", "KENNTNISSE", "KOMPETENZEN"],
    }

    for section, keywords in required.items():
        if not any(kw in text_upper for kw in keywords):
            issues.append({
                "issue": f"Standard section missing: {section}",
                "severity": "medium"
            })

    return issues


def _check_special_characters(cv_text: str) -> List[Dict]:
    """Check for characters that commonly break ATS parsers."""
    issues = []
    problematic = ['★', '●', '■', '►', '✓', '✗', '→', '©', '®']
    found = [c for c in problematic if c in cv_text]
    if found:
        issues.append({
            "issue": f"Special characters found that may break ATS: {' '.join(found)}",
            "severity": "low"
        })
    return issues


def _calculate_score(issues: List[Dict]) -> int:
    """Deduct points per issue severity. Score cannot go below 0."""
    score = 100
    deductions = {"high": 25, "medium": 15, "low": 5}
    for issue in issues:
        score -= deductions.get(issue.get("severity", "low"), 5)
    return max(0, score)


def _get_recommendation(score: int) -> str:
    if score >= 80:
        return "CV is ATS-friendly"
    if score >= 60:
        return "CV has minor ATS issues — review before submitting"
    return "CV has significant ATS issues — fix before submitting"