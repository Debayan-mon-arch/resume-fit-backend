import fitz
from docx import Document
import re

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

# --- Department + Level mapping to core keywords ---
ROLE_KEYWORDS = {
    ("admin", "executive"): {
        "skills": ["coordination", "scheduling", "facility"],
        "tools": ["excel"],
        "domain": ["admin operations"],
        "education": ["graduate"]
    },
    ("b2b", "senior executive"): {
        "skills": ["partner management", "negotiation", "relationship building"],
        "tools": ["crm", "excel"],
        "domain": ["b2b sales", "enterprise"],
        "education": ["bba", "mba"]
    },
    ("b2c", "am"): {
        "skills": ["telecalling", "lead conversion", "customer handling"],
        "tools": ["dialer", "crm"],
        "domain": ["direct sales", "b2c"],
        "education": ["bcom", "graduate"]
    },
    ("human resources", "vp"): {
        "skills": ["hr strategy", "org design", "policy making"],
        "tools": ["workday", "successfactors"],
        "domain": ["hr leadership"],
        "education": ["mba hr"]
    },
    ("technology", "sm"): {
        "skills": ["backend", "architecture", "design patterns"],
        "tools": ["java", "docker", "aws"],
        "domain": ["software engineering"],
        "education": ["btech", "mtech"]
    },
    # Add more department-level entries as required
}

# --- Helper: expand synonyms ---
def expand_keywords(keywords):
    expanded = set()
    for word in keywords:
        word = word.lower().strip()
        expanded.add(word)
        if word in SYNONYMS:
            expanded.update(SYNONYMS[word])
    return list(expanded)

# --- Get expanded profile keyword set ---
def get_profile_keywords(department, level):
    key = (department.lower(), level.strip())
    keywords = ROLE_KEYWORDS.get(key, {})
    return {
        field: expand_keywords(keywords.get(field, [])) for field in ["skills", "tools", "domain", "education"]
    }

# --- Extract loose keywords from parsed text ---
def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    return {
        "skills": [w.strip().lower() for w in words if len(w.strip()) > 2],
        "tools": [],
        "domain": [],
        "education": []
    }
