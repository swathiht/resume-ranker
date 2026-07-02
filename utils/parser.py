# utils/parser.py
# Day 2 — Resume Section Parser

import re

# =============================================
# PART 1 — SECTION DETECTOR
# =============================================

def extract_sections(text):
    """
    Splits resume text into sections like
    Skills, Education, Experience, Projects
    """
    # Common section headings in resumes
    section_keywords = [
        "EDUCATION", "ACADEMIC PROJECTS", "PROJECTS",
        "SKILLS", "EXPERIENCE", "WORK EXPERIENCE",
        "CERTIFICATES", "ACHIEVEMENTS", "EXTRACURRICULAR",
        "INTERNSHIP", "SUMMARY", "OBJECTIVE"
    ]

    sections = {}
    current_section = "HEADER"
    sections[current_section] = []

    for line in text.splitlines():
        line_upper = line.strip().upper()

        # Check if this line is a section heading
        matched = False
        for keyword in section_keywords:
            if keyword in line_upper and len(line.strip()) < 50:
                current_section = keyword
                sections[current_section] = []
                matched = True
                break

        if not matched and line.strip():
            sections[current_section].append(line.strip())

    # Join each section into a single string
    for key in sections:
        sections[key] = '\n'.join(sections[key])

    return sections


# =============================================
# PART 2 — CONTACT INFO EXTRACTORS
# =============================================

def extract_email(text):
    """Extract email address from resume"""
    pattern = r'[\w.+-]+@[\w-]+\.[a-zA-Z]+'
    match = re.findall(pattern, text)
    return match[0] if match else "Not found"


def extract_phone(text):
    """Extract phone number from resume"""
    pattern = r'[\+]?[\d\s\-]{10,15}'
    match = re.findall(pattern, text)
    return match[0].strip() if match else "Not found"

def extract_name(text):
    """
    Extract candidate name
    Usually the first non-empty line of resume
    """
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        # Skip empty lines, page markers, short lines
        if line and "Page" not in line and len(line) > 3:
            # If line has | symbol, take only the part before it
            if "|" in line:
                line = line.split("|")[0].strip()
            # If line has email in it, skip it
            if "@" in line:
                continue
            return line
    return "Not found"



# =============================================
# PART 3 — FULL PARSER
# =============================================

def parse_resume(text):
    """
    Full resume parser — returns all info in one dict
    """
    sections = extract_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "sections": sections
    }