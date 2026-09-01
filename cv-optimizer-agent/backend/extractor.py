import pdfplumber
from docx import Document

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return _extract_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return _extract_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def _extract_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages).strip()

def _extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )