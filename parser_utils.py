import fitz
from docx import Document

# --- PDF & DOCX text extractor ---
def extract_text(file_storage):
    try:
        filename = file_storage.filename.lower()
        text = ""
        if filename.endswith(".pdf"):
            file_storage.stream.seek(0)
            doc = fitz.open(stream=file_storage.read(), filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        elif filename.endswith(".docx"):
            file_storage.stream.seek(0)
            doc = Document(file_storage)
            text = " ".join(p.text for p in doc.paragraphs)
        return text.replace("\n", " ").strip().lower()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# --- Synonym-mapped profile keywords ---
ROLE_KEYWORDS = {
    ("tech", "L3"): {
        "skills": ["python", "java", "data structures", "algorithms", "oop", "backend development"],
        "tools": ["git", "docker", "kubernetes", "vscode", "jenkins"],
        "domain": ["software engineering", "cloud", "api design"],
        "education": ["btech", "mtech", "b.e", "b.sc computer science"]
    },
    ("hr", "L2"): {
        "skills": ["recruitment", "employee relations", "onboarding", "exit interviews"],
        "tools": ["excel", "workday", "successfactors"],
        "domain": ["human resources", "people operations"],
        "education": ["mba hr", "pgdm", "bba hr"]
    },
    ("marketing", "L1"): {
        "skills": ["content creation", "campaign execution", "brand communication"],
        "tools": ["canva", "google ads", "meta business suite"],
        "domain": ["digital marketing", "performance marketing"],
        "education": ["bba", "mba marketing"]
    }
    # Add more (dept, level) mappings as needed
}

# --- Synonym bank ---
SYNONYMS = {
    "python": ["py", "python3", "scripting"],
    "git": ["gitlab", "github"],
    "docker": ["containers"],
    "cloud": ["aws", "azure", "gcp", "cloud infra"],
    "recruitment": ["talent acquisition", "hiring"],
    "employee relations": ["grievance", "hrbp"],
    "content creation": ["copywriting", "social content", "posts", "reels"],
    "performance marketing": ["paid ads", "ppc", "media buying"],
    "campaign execution": ["campaign mgmt", "brand activation"]
}
import re

# --- Helper: expand synonyms into flat list ---
def expand_keywords(keywords):
    expanded = set()
    for kw in keywords:
        kw = kw.strip().lower()
        expanded.add(kw)
        if kw in SYNONYMS:
            expanded.update(SYNONYMS[kw])
    return list(expanded)

# --- Extract profile keywords by dept + level ---
def get_profile_keywords(dept, level):
    key = (dept.lower(), level.upper())
    role = ROLE_KEYWORDS.get(key, {})
    return {
        field: expand_keywords(role.get(field, []))
        for field in ["skills", "tools", "domain", "education"]
    }

# --- Extract keywords from CV/JD text if needed ---
def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    return [w.strip().lower() for w in words if len(w.strip()) > 2]
