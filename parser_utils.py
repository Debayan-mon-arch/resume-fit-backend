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
    "compliance": ["legal", "regulatory", "audit"]
}
# --- Role Keyword Mapping (Dept, Level) aligned with front-end dropdowns ---
ROLE_KEYWORDS = {
    ("technology", "senior executive"): {
        "skills": ["python", "java", "system design", "data structures"],
        "tools": ["git", "docker", "kubernetes", "vscode"],
        "domain": ["backend engineering", "cloud"],
        "education": ["btech", "mtech", "b.e"]
    },
    ("marketing", "manager"): {
        "skills": ["branding", "seo", "campaign execution", "performance marketing"],
        "tools": ["google ads", "meta business suite", "canva"],
        "domain": ["digital marketing"],
        "education": ["mba marketing", "bba"]
    },
    ("human resources", "am"): {
        "skills": ["recruitment", "employee relations", "onboarding", "exit interviews"],
        "tools": ["excel", "workday", "successfactors"],
        "domain": ["people operations", "talent engagement"],
        "education": ["mba hr", "pgdm", "bba"]
    },
    ("b2b", "senior executive"): {
        "skills": ["negotiation", "partner acquisition", "sales pipeline"],
        "tools": ["crm", "excel"],
        "domain": ["enterprise sales", "channel sales"],
        "education": ["mba", "bcom"]
    },
    ("b2c", "executive"): {
        "skills": ["telecalling", "lead conversion", "upselling"],
        "tools": ["dialer", "leadsquared"],
        "domain": ["inbound sales", "d2c"],
        "education": ["graduate", "bba"]
    },
    ("finance", "manager"): {
        "skills": ["p&l", "budgeting", "financial modeling"],
        "tools": ["tally", "excel"],
        "domain": ["corporate finance"],
        "education": ["ca", "mba finance"]
    },
    ("compliance", "avp"): {
        "skills": ["audit", "regulatory compliance", "risk control"],
        "tools": ["compliance tracker", "ms excel"],
        "domain": ["legal compliance", "internal control"],
        "education": ["llb", "mba"]
    },
    ("product", "am"): {
        "skills": ["product roadmap", "requirement gathering", "design sprint"],
        "tools": ["jira", "figma", "trello"],
        "domain": ["ux", "product management"],
        "education": ["btech", "mba"]
    },
    ("strategy & analytics", "manager"): {
        "skills": ["forecasting", "dashboarding", "competitive analysis"],
        "tools": ["powerbi", "excel", "sql"],
        "domain": ["market strategy", "data analytics"],
        "education": ["mba", "statistics"]
    },
    ("operations", "dm"): {
        "skills": ["sla tracking", "process improvement", "workflow automation"],
        "tools": ["excel", "as400", "sap"],
        "domain": ["service delivery", "ops mgmt"],
        "education": ["bcom", "mba"]
    },
    ("supply", "manager"): {
        "skills": ["logistics coordination", "inventory mgmt", "warehouse ops"],
        "tools": ["erp", "excel"],
        "domain": ["supply chain"],
        "education": ["btech", "mba supply"]
    },
    ("claims, inbound & onboarding", "executive"): {
        "skills": ["claim processing", "documentation", "customer handling"],
        "tools": ["crm", "email", "excel"],
        "domain": ["insurance process"],
        "education": ["graduate"]
    },
    ("cross sell", "sm"): {
        "skills": ["upselling", "cross promotion", "retargeting"],
        "tools": ["excel", "crm"],
        "domain": ["retail", "b2c"],
        "education": ["mba", "bba"]
    },
    ("legal", "manager"): {
        "skills": ["contract drafting", "compliance", "case tracking"],
        "tools": ["word", "compliance systems"],
        "domain": ["corporate law", "legal ops"],
        "education": ["llb"]
    },
    ("learning & development", "am"): {
        "skills": ["training delivery", "learning need analysis", "e-learning"],
        "tools": ["lms", "ppt", "excel"],
        "domain": ["capability building"],
        "education": ["pgdm", "mba hr"]
    },
    ("reinsurance", "manager"): {
        "skills": ["underwriting", "reinsurance treaties", "loss ratio"],
        "tools": ["excel"],
        "domain": ["risk underwriting"],
        "education": ["actuarial science", "mba insurance"]
    },
    ("admin", "executive"): {
        "skills": ["facility management", "vendor mgmt", "coordination"],
        "tools": ["excel"],
        "domain": ["admin operations"],
        "education": ["graduate"]
    },
    ("customer excellence", "manager"): {
        "skills": ["customer journey", "feedback resolution", "nps"],
        "tools": ["zendesk", "email tools", "crm"],
        "domain": ["cx", "service excellence"],
        "education": ["mba"]
    },
    ("founder's office", "avp"): {
        "skills": ["special projects", "business research", "planning"],
        "tools": ["ppt", "excel", "powerbi"],
        "domain": ["founder support"],
        "education": ["mba", "btech"]
    },
    ("revenue", "sm"): {
        "skills": ["pricing", "growth analysis", "sales funnel"],
        "tools": ["crm", "excel"],
        "domain": ["topline mgmt"],
        "education": ["mba"]
    }
}

# --- Helper: Synonym Expander ---
def expand_keywords(keywords):
    expanded = set()
    for kw in keywords:
        kw = kw.strip().lower()
        expanded.add(kw)
        if kw in SYNONYMS:
            expanded.update(SYNONYMS[kw])
    return list(expanded)

# --- Get profile keywords based on department & level ---
def get_profile_keywords(dept, level):
    key = (dept.lower(), level.lower())
    keywords = ROLE_KEYWORDS.get(key, {})
    return {
        field: expand_keywords(keywords.get(field, [])) for field in ["skills", "tools", "domain", "education"]
    }

# --- Extract keywords from JD or CV text ---
def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    filtered = [w.strip().lower() for w in words if len(w.strip()) > 2]
    return {
        "skills": filtered,
        "tools": [],
        "domain": [],
        "education": []
    }
