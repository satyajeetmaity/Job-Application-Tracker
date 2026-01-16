from pdfminer.high_level import extract_text

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF resume.
       Returns plain text string."""
    try:
        text = extract_text(file_path)
        if not text:
            return ""
        return text.strip()
    except Exception as e:
        return ""