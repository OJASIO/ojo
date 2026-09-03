import pymupdf
import unicodedata
import re
from docx import Document

# Only truly non-standard characters need manual mapping
# Standard ligatures (fi, fl, ff etc) are handled by NFKC automatically
CUSTOM_LIGATURES = {
    '\u019F': 'ti',      # Ɵ — misused as ti ligature
    '\u01A9': 'tt',      # Ʃ — misused as tt ligature
    '\u0145': 'fk',      # Ņ — misused as fk ligature
    '\u019E': 'tf',      # ƞ — misused as tf ligature
    '\u014C': 'ft',      # Ō — misused as ft ligature
    '\uF0B7': '\u2022',  # private use bullet → standard bullet
}


def fix_encoding(text: str) -> str:
    """
    Two-step encoding fix:
    Step 1 — NFKC normalisation handles ALL standard Unicode ligatures
    Step 2 — Custom map handles non-standard characters
    """
    text = unicodedata.normalize('NFKC', text)
    for char, replacement in CUSTOM_LIGATURES.items():
        text = text.replace(char, replacement)
    return text


def extract_name_from_pdf(file_path: str) -> str:
    """
    Extract the candidate name using font size.
    The name in a CV is almost always the largest text
    on the first page. Works for ALL CAPS, title case,
    any language, any format — no NER needed.
    """
    doc = pymupdf.open(file_path)
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    candidates = []
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                size = span["size"]
                words = text.split()
                # Name criteria:
                # 1 to 4 words
                # no special characters that indicate not a name
                # meaningful length
                if (1 <= len(words) <= 4
                        and len(text) > 3
                        and not any(c in text for c in
                                    ['@', '/', '|', ':', '+',
                                     '(', ')', '.com', 'http',
                                     '.de', '.pdf', '·', '–'])):
                    candidates.append((size, text))

    doc.close()

    if not candidates:
        return ""

    # Return the text with the largest font size
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return _extract_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return _extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")


def _extract_pdf(file_path: str) -> str:
    doc = pymupdf.open(file_path)
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()
    raw = "\n".join(pages).strip()
    return fix_encoding(raw)


def _extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    raw = "\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )
    return fix_encoding(raw)