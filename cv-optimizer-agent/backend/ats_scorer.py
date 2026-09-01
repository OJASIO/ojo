# ─────────────────────────────────────────────────────────────────────────────
# ats_scorer.py  —  Check how well the CV will parse in ATS systems
# ATS (Applicant Tracking Systems) are used by most employers to screen CVs.
# Many CVs fail at this stage before a human ever reads them.
# ─────────────────────────────────────────────────────────────────────────────

ATS_BREAKING_PATTERNS = [
    "\t",          # Tabs (often from table-based layouts)
    "|",             # Pipe characters (from table borders)
]

STANDARD_SECTIONS_EN = ["experience", "education", "skills", "summary", "contact"]
STANDARD_SECTIONS_DE = ["berufserfahrung", "ausbildung", "kenntnisse", "kontakt"]


def calculate_ats_score(cv_text: str, lang: str) -> int:
    """
    Calculate an ATS compatibility score from 0-100.
    Higher score = more ATS friendly.

    Scoring logic (implement one by one):
      - Start at 100
      - Subtract 20 if tables detected (pipe chars / heavy tab usage)
      - Subtract 15 if contact info looks like it is in a header
      - Subtract 10 for each non-standard section title (max -20)
      - Subtract 5 if no standard section titles found at all
      - Never go below 0

    TODO: Implement scoring logic
    """
    # TODO: Implement
    score = 100
    return max(0, score)


def detect_table_usage(cv_text: str) -> bool:
    """
    Detect if the CV likely uses tables for layout.
    Tables are invisible in the final PDF but break ATS text extraction.

    TODO:
      - Check if text contains many pipe characters (|)
      - Check for tab-separated columns
      - Return True if likely table-based layout
    """
    # TODO: Implement
    pass


def get_ats_issues(cv_text: str, lang: str) -> list[str]:
    """
    Return a list of human-readable ATS compatibility issues found.

    TODO:
      - Check for table usage
      - Check if contact info is in extractable location
      - Check for non-standard section titles
      - Return list of issue strings (empty list if all clear)
    """
    # TODO: Implement
    issues = []
    return issues
