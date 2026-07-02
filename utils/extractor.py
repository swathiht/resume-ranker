# utils/extractor.py
# Handles PDF, DOCX, DOC, TXT formats

import fitz           # for PDF
import docx           # for DOCX
import os


# =============================================
# PART 1 — FORMAT DETECTORS
# =============================================

def get_file_extension(file_path):
    """
    Detects file format from extension
    Example: "resume.pdf" → ".pdf"
    """
    _, extension = os.path.splitext(file_path)
    return extension.lower()


# =============================================
# PART 2 — INDIVIDUAL EXTRACTORS
# =============================================

def extract_from_pdf(file_path):
    """
    Extracts text from PDF file using PyMuPDF
    """
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page_num, page in enumerate(doc):
            text = page.get_text()
            full_text += f"\n--- Page {page_num + 1} ---\n"
            full_text += text
        doc.close()
        return full_text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_from_docx(file_path):
    """
    Extracts text from Word DOCX file
    """
    try:
        doc = docx.Document(file_path)
        full_text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text += paragraph.text + "\n"
        return full_text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


def extract_from_txt(file_path):
    """
    Extracts text from plain TXT file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"


# =============================================
# PART 3 — SMART UNIVERSAL EXTRACTOR
# =============================================

def extract_text(file_path):
    """
    Universal extractor — detects format automatically
    and calls the right extractor

    Supports: PDF, DOCX, TXT
    """
    extension = get_file_extension(file_path)

    if extension == ".pdf":
        print(f"📄 Detected: PDF file")
        return extract_from_pdf(file_path)

    elif extension == ".docx":
        print(f"📝 Detected: Word DOCX file")
        return extract_from_docx(file_path)

    elif extension == ".txt":
        print(f"📃 Detected: Text file")
        return extract_from_txt(file_path)

    else:
        return f"❌ Unsupported format: {extension}\nSupported: PDF, DOCX, TXT"


# =============================================
# PART 4 — CLEANER (same as before)
# =============================================

def clean_text(text):
    """
    Cleans extracted text
    Removes extra spaces and blank lines
    """
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return '\n'.join(cleaned)


def extract_and_clean(file_path):
    """
    Full pipeline: detect format → extract → clean
    Works for PDF, DOCX, TXT
    """
    raw_text = extract_text(file_path)
    cleaned_text = clean_text(raw_text)
    return cleaned_text