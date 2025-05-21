import fitz  # for PDF
from docx import Document
import re

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        return " ".join([page.get_text() for page in doc])
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return " ".join([p.text for p in doc.paragraphs])
    return ""

def extract_fields(file_path):
    text = extract_text(file_path).lower()

    # Core Fields
    skills = [w for w in ["communication", "analysis", "sales", "negotiation", "python", "excel", "sql"] if w in text]
    domain = [w for w in ["finance", "hr", "supply chain", "marketing"] if w in text]
    tools = [w for w in ["excel", "sql", "powerbi", "tableau"] if w in text]
    education = [w for w in ["mba", "btech", "bba", "ssc", "hsc", "10th", "12th"] if w in text]

    # Optional Fields (basic regex or phrase checks)
    experience = extract_experience(text)
    joining = extract_joining(text)
    age = extract_age(text)
    gender = "female" if "female" in text else "male" if "male" in text else ""
    graduate = "pg" if "pg" in text else "ug" if "ug" in text else ""

    return {
        "skills": skills,
        "domain": domain,
        "tools": tools,
        "education": education,
        "experience": experience,
        "joining": joining,
        "age": age,
        "gender": gender,
        "graduate": graduate
    }

def extract_experience(text):
    match = re.search(r"(\\d+)\\s*(years|yrs)", text)
    return int(match.group(1)) if match else None

def extract_joining(text):
    for key in ["immediate", "10 days", "30 days", "1 month", "2 month", "3 month"]:
        if key in text:
            return key
    return ""

def extract_age(text):
    match = re.search(r"(age[:\\s]+)?(\\d{2})", text)
    return int(match.group(2)) if match else None