import fitz
from docx import Document
import re

# --- PDF/DOCX Text Extraction ---
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

# --- Synonym Bank ---
SYNONYMS = {
    "python": ["py", "python3", "scripting"],
    "git": ["gitlab", "github"],
    "docker": ["containers"],
    "cloud": ["aws", "azure", "gcp", "cloud infra"],
    "recruitment": ["talent acquisition", "hiring"],
    "employee relations": ["grievance", "hrbp"],
    "content creation": ["copywriting", "social content", "posts", "reels"],
    "performance marketing": ["paid ads", "ppc", "media buying"],
    "campaign execution": ["campaign mgmt", "brand activation"],
    "compliance": ["risk", "regulations"],
    "strategy": ["strategic", "planning"],
    "analytics": ["data", "dashboards", "metrics"],
    "finance": ["accounting", "p&l", "budgeting"],
    "sales": ["targets", "pipeline", "conversion", "revenue"],
    "hr": ["onboarding", "exit", "retention", "training"],
    "technology": ["devops", "infra", "architecture"],
    "b2b": ["enterprise", "partner", "client"],
    "b2c": ["consumer", "customer", "d2c"],
    "supply": ["logistics", "inventory", "delivery"],
    "renewal": ["retention", "follow-up"],
    "marketing": ["campaign", "branding", "seo"],
    "product": ["ux", "roadmap", "feature"]
}
# --- Role Keyword Mapping by (Department, Level) ---
ROLE_KEYWORDS = {
    ("tech", "l3"): {
        "skills": ["python", "java", "data structures", "algorithms"],
        "tools": ["git", "docker", "vscode"],
        "domain": ["software engineering", "cloud"],
        "education": ["btech", "mtech", "b.e", "b.sc computer science"]
    },
    ("hr", "l2"): {
        "skills": ["recruitment", "employee relations", "onboarding"],
        "tools": ["excel", "workday"],
        "domain": ["human resources", "people operations"],
        "education": ["mba hr", "pgdm", "bba hr"]
    },
    ("marketing", "l1"): {
        "skills": ["content creation", "campaign execution"],
        "tools": ["canva", "google ads"],
        "domain": ["digital marketing"],
        "education": ["bba", "mba marketing"]
    },
    ("b2b", "senior executive"): {
        "skills": ["negotiation", "partner onboarding"],
        "tools": ["excel", "crm"],
        "domain": ["sales", "distribution"],
        "education": ["bcom", "mba"]
    },
    ("b2c", "am"): {
        "skills": ["telecalling", "lead conversion", "inside sales"],
        "tools": ["dialer", "lead square", "excel"],
        "domain": ["b2c", "d2c"],
        "education": ["graduate", "bba"]
    },
    # Add more mappings as needed
}

# --- Helper: Expand keywords using synonyms ---
def expand_keywords(keywords):
    expanded = set()
    for kw in keywords:
        kw = kw.strip().lower()
        expanded.add(kw)
        if kw in SYNONYMS:
            expanded.update(SYNONYMS[kw])
    return list(expanded)

# --- Get mapped keywords for a role ---
def get_profile_keywords(dept, level):
    key = (dept.lower(), level.lower())
    role = ROLE_KEYWORDS.get(key, {})
    return {
        field: expand_keywords(role.get(field, []))
        for field in ["skills", "tools", "domain", "education"]
    }

# --- Extract keywords from unstructured text (JD/CV) ---
def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    cleaned = [w.strip().lower() for w in words if len(w.strip()) > 2]
    return {
        "skills": cleaned,
        "tools": [],
        "domain": [],
        "education": []
    }
