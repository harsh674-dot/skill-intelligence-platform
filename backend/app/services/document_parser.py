from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract plain text from a supported learning-content file.
    """

    file_type = file_type.lower().replace(".", "")

    if file_type == "pdf":
        return _extract_pdf(file_path)

    if file_type == "docx":
        return _extract_docx(file_path)

    if file_type == "txt":
        return _extract_txt(file_path)

    raise ValueError(
        f"Unsupported file type: {file_type}. "
        "Supported types: pdf, docx, txt"
    )


def _extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages).strip()


def _extract_docx(file_path: str) -> str:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs).strip()


def _extract_txt(file_path: str) -> str:
    return Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore",
    ).strip()