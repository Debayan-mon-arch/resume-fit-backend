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
    "branding": ["brand", "identity", "positioning"],
    "content creation": ["copywriting", "social content", "reels"],
    "campaign execution": ["campaign mgmt", "brand activation"],
    "compliance": ["risk", "regulations", "audit"],
    "strategy": ["strategic", "planning", "roadmap"],
    "analytics": ["data", "dashboards", "metrics"],
    "finance": ["accounting", "p&l", "budgeting"],
    "sales": ["targets", "pipeline", "conversion", "revenue"],
    "hr": ["onboarding", "exit", "retention", "training"],
    "technology": ["devops", "infra", "architecture", "it systems"],
    "b2b": ["enterprise", "partner", "channel sales"],
    "b2c": ["consumer", "customer", "d2c"],
    "supply": ["logistics", "inventory", "fulfillment"],
    "renewal": ["retention", "follow-up", "lifecycle"],
    "marketing": ["seo", "sem", "campaign"],
    "product": ["ux", "feature", "roadmap"],
    "excel": ["spreadsheets", "ms excel"],
    "sql": ["queries", "database"],
    "lead conversion": ["lead closing", "closure"],
    "crm": ["hubspot", "salesforce", "zoho"],
    "insights": ["analytics", "dashboards"]
}
# --- Role Keyword Mapping (Dept, Level) aligned with frontend ---
ROLE_KEYWORDS = {
    ("technology", "senior executive"): {
        "skills": ["python", "java", "system design", "data structures"],
        "tools": ["git", "docker", "kubernetes", "vscode"],
        "domain": ["backend engineering", "cloud"],
        "education": ["btech", "mtech", "b.e"]
    },
    ("human resources", "am"): {
        "skills": ["recruitment", "employee relations", "onboarding"],
        "tools": ["excel", "workday"],
        "domain": ["people operations", "talent management"],
        "education": ["mba hr", "pgdm", "bba"]
    },
    ("marketing", "manager"): {
        "skills": ["branding", "seo", "campaign execution"],
        "tools": ["google ads", "meta", "canva"],
        "domain": ["digital marketing", "performance marketing"],
        "education": ["mba marketing", "bba"]
    },
    ("b2b", "senior executive"): {
        "skills": ["negotiation", "partner onboarding", "pipeline building"],
        "tools": ["crm", "excel"],
        "domain": ["enterprise sales", "distribution"],
        "education": ["mba", "bcom"]
    },
    ("b2c", "executive"): {
        "skills": ["telecalling", "lead conversion", "upselling"],
        "tools": ["dialer", "lead square"],
        "domain": ["inbound sales", "retail"],
        "education": ["graduate", "bba"]
    },
    ("compliance", "avp"): {
        "skills": ["regulatory reporting", "audit", "risk control"],
        "tools": ["compliance tracker", "excel"],
        "domain": ["legal compliance", "internal audit"],
        "education": ["llb", "mba"]
    },
    ("strategy & analytics", "manager"): {
        "skills": ["forecasting", "dashboarding", "competitive analysis"],
        "tools": ["powerbi", "sql", "excel"],
        "domain": ["market research", "data strategy"],
        "education": ["mba", "statistics"]
    },
    ("operations", "dm"): {
        "skills": ["sla tracking", "workflow", "process optimization"],
        "tools": ["as400", "sap"],
        "domain": ["ops mgmt", "service delivery"],
        "education": ["mba", "bcom"]
    },
    ("supply", "manager"): {
        "skills": ["inventory", "logistics", "warehouse ops"],
        "tools": ["erp", "excel"],
        "domain": ["supply chain"],
        "education": ["btech", "mba supply"]
    }
    # Add more department–level combos as needed
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

# --- Get mapped keywords for department & level ---
def get_profile_keywords(dept, level):
    key = (dept.lower(), level.lower())
    role = ROLE_KEYWORDS.get(key, {})
    return {
        field: expand_keywords(role.get(field, []))
        for field in ["skills", "tools", "domain", "education"]
    }

# --- Extract keywords from JD or CV (text blob) ---
def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    filtered = [w.strip().lower() for w in words if len(w.strip()) > 2]
    return {
        "skills": filtered,
        "tools": filtered,
        "domain": filtered,
        "education": filtered
    }
