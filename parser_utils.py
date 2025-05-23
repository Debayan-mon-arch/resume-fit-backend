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
    "python": ["py", "python3", "scripting", "backend scripting"],
    "git": ["gitlab", "github", "version control"],
    "docker": ["containers", "containerization"],
    "cloud": ["aws", "azure", "gcp", "cloud infra", "cloud architecture"],
    "recruitment": ["talent acquisition", "hiring", "staffing", "headhunting"],
    "employee relations": ["grievance", "hrbp", "employee engagement", "people mgmt"],
    "branding": ["brand", "identity", "positioning", "rebranding"],
    "content creation": ["copywriting", "social content", "reels", "posts", "creative writing"],
    "campaign execution": ["campaign mgmt", "brand activation", "ad launch", "promotion"],
    "compliance": ["risk", "regulations", "audit", "regulatory", "legal"],
    "strategy": ["strategic", "planning", "roadmap", "vision", "go-to-market"],
    "analytics": ["data", "dashboards", "metrics", "visualization", "reporting"],
    "finance": ["accounting", "p&l", "budgeting", "forecasting", "cost control"],
    "sales": ["targets", "pipeline", "conversion", "revenue", "upselling", "leads"],
    "hr": ["onboarding", "exit", "retention", "training", "employee lifecycle"],
    "technology": ["devops", "infra", "architecture", "it systems", "backend", "systems design"],
    "b2b": ["enterprise", "partner", "channel sales", "corporate sales"],
    "b2c": ["consumer", "customer", "d2c", "retail sales"],
    "supply": ["logistics", "inventory", "fulfillment", "procurement", "dispatch"],
    "renewal": ["retention", "follow-up", "lifecycle", "policy renewal"],
    "marketing": ["seo", "sem", "campaign", "adwords", "brand mgmt"],
    "product": ["ux", "feature", "roadmap", "requirement gathering", "release planning"],
    "training": ["learning", "l&d", "skills building", "e-learning"],
    "crm": ["salesforce", "zoho", "hubspot", "lead mgmt"],
    "customer service": ["support", "queries", "client care", "inbound calls"],
    "negotiation": ["deal closure", "pricing discussion", "bargaining"],
    "lead generation": ["prospecting", "cold calling", "inbound leads", "outreach"],
    "telecalling": ["calling", "voice process", "phone sales"],
    "excel": ["spreadsheets", "formulas", "pivot tables", "vlookup"],
    "powerpoint": ["presentations", "slides", "ppt"],
    "erp": ["sap", "oracle", "ms dynamics", "netsuite"],
    "legal": ["contract", "litigation", "compliance", "corporate law"],
    "vendor management": ["supplier mgmt", "third party", "procurement"],
    "forecasting": ["prediction", "modeling", "trend analysis"],
    "insurance": ["policy", "claim", "premium", "underwriting"],
    "cx": ["customer experience", "nps", "feedback", "csat", "customer experience", "service quality", "satisfaction"],
    "lms": ["learning system", "elearning", "online courses"],
    "dashboarding": ["visualization", "reporting", "kpi tracker"],
    "automation": ["bots", "scripts", "workflow tools", "rpa"],
    "sql": ["structured query", "database query", "postgres", "mysql"],
    "presentation": ["slides", "decks", "ppt"],
    "contract": ["agreement", "mou", "legal document"],
    "coordination": ["scheduling", "follow-ups", "team sync"],
    "operations": ["ops", "daily mgmt", "service delivery"],
    "client": ["customer", "stakeholder", "partner"],
    "admin": ["facilities", "office mgmt", "support staff", "vendor liaison"],
    "research": ["analysis", "insights", "study", "evaluation"],
    "performance marketing": ["paid ads", "cpc", "ppc", "google ads", "meta ads"],
    "graphic design": ["visuals", "illustrations", "branding", "canva"],
    "email marketing": ["mailchimp", "newsletter", "campaign"],
    "field sales": ["on-ground", "door-to-door", "feet-on-street"],
    "internal audit": ["compliance check", "risk control", "process audit"],
    "training delivery": ["facilitation", "classroom", "skill transfer"],
    "claims": ["reimbursements", "settlements", "processing"],
    "policy": ["insurance", "coverage", "benefits"],
    "ecommerce": ["online retail", "shopping", "cart"],
    "project mgmt": ["scrum", "agile", "kanban", "milestones"],
    "support": ["service desk", "helpdesk", "ticket"],
    "leadership": ["people mgmt", "team lead", "supervisor"],
    "documentation": ["sop", "manual", "handbook"],
    "planning": ["roadmap", "timeline", "blueprint"],
    "pricing": ["costing", "valuation", "quote"],
    "growth": ["scaling", "expansion", "go-to-market"],
    "ux": ["ui", "user experience", "interaction design"],
    "revenue": ["income", "sales", "billing"],
    "strategy": ["approach", "tactics", "plan"],
    "business development": ["bd", "sales", "client acquisition"],
    "founder support": ["ceo office", "special projects", "executive support"],
    "comms": ["communication", "emails", "presentations"],
    "social media": ["facebook", "instagram", "linkedin", "twitter"],
    "inventory": ["stock", "goods", "items"],
    "campaign": ["promo", "advertising", "outreach"]
}



# --- Role Keyword Mapping (Dept, Level) aligned with frontend ---
ROLE_KEYWORDS = {
    ("technology", "senior executive"): {
        "skills": ["python", "java", "system design", "data structures", "oop", "rest apis", "agile", "testing", "debugging", "scalability"],
        "tools": ["git", "docker", "kubernetes", "vscode", "jenkins", "intellij", "postman", "jira", "confluence", "linux"],
        "domain": ["backend engineering", "frontend dev", "cloud systems", "distributed systems", "devops", "microservices", "infra ops", "database management", "app security", "api gateway"],
        "education": ["btech", "mtech", "b.e", "b.sc computer science", "mca", "bca", "btech it", "btech cse", "msc cs", "pg diploma in cs"]
    },
    ("marketing", "manager"): {
        "skills": ["branding", "seo", "sem", "campaign execution", "performance marketing", "market research", "go-to-market", "demand gen", "email marketing", "influencer marketing"],
        "tools": ["google ads", "meta business suite", "canva", "mailchimp", "hubspot", "google analytics", "ahrefs", "semrush", "figma", "hootsuite"],
        "domain": ["digital marketing", "brand management", "media planning", "consumer behavior", "content marketing", "retail marketing", "btl/atl marketing", "pr", "brand activation", "community building"],
        "education": ["mba marketing", "bba", "pgdm marketing", "mass comm", "advertising diploma", "bmm", "ba communication", "mba comms", "mba digital", "bms"]
    },
    ("human resources", "am"): {
        "skills": ["recruitment", "employee relations", "onboarding", "exit interviews", "hr policies", "performance appraisal", "talent acquisition", "succession planning", "grievance handling", "hr audits"],
        "tools": ["excel", "workday", "successfactors", "greytHR", "zoho people", "darwinbox", "naukri", "linkedin recruiter", "keka", "bambooHR"],
        "domain": ["people operations", "talent engagement", "employee experience", "hr analytics", "l&d", "comp & ben", "labor law", "industrial relations", "org development", "hrbp"],
        "education": ["mba hr", "pgdm hr", "bba hr", "ma psychology", "msw", "ba sociology", "mba ob", "bcom hr", "mba l&d", "mba ir"]
    },
    ("finance", "manager"): {
        "skills": ["budgeting", "forecasting", "variance analysis", "financial modeling", "fund flow", "p&l", "accounting", "cash flow", "roi analysis", "payroll mgmt"],
        "tools": ["tally", "excel", "quickbooks", "zoho books", "sap fico", "oracle finance", "powerbi", "erp", "netsuite", "busy accounting"],
        "domain": ["corporate finance", "accounting & audit", "financial control", "statutory compliance", "taxation", "treasury", "internal audit", "budget planning", "working capital mgmt", "cost control"],
        "education": ["ca", "mba finance", "cfa", "icwa", "bcom", "mcom", "cs", "pg diploma in finance", "bba finance", "acca"]
    },
    ("b2b", "senior executive"): {
        "skills": ["negotiation", "partner acquisition", "sales pipeline", "lead qualification", "cold calling", "crm hygiene", "proposal writing", "demo pitching", "cross-sell", "key account mgmt"],
        "tools": ["excel", "salesforce", "zoho crm", "hubspot", "outreach", "linkedin sales navigator", "ppt", "aircall", "mailmerge", "whatsapp web"],
        "domain": ["enterprise sales", "channel sales", "partnership onboarding", "account-based marketing", "reseller mgmt", "pre-sales", "post-sales support", "b2b marketing", "inside sales", "field sales"],
        "education": ["mba sales", "bcom", "mba marketing", "pgdm sales", "bba", "ba economics", "mba b2b", "bsc", "mba ib", "mba comm"]
    },
    ("b2c", "executive"): {
        "skills": ["telecalling", "lead conversion", "upselling", "objection handling", "product pitching", "follow-ups", "customer onboarding", "demo scheduling", "sales scripts", "crm entry"],
        "tools": ["dialer", "leadsquared", "zoho crm", "excel", "call recorder", "outlook", "freshdesk", "aircall", "salesforce", "sms blast"],
        "domain": ["inbound sales", "tele-sales", "consumer onboarding", "support transition", "b2c funnel", "retention", "direct sales", "field conversion", "d2c", "post-sale services"],
        "education": ["graduate", "bba", "ba", "bcom", "bca", "pg diploma", "mba", "diploma in sales", "mass comm", "bmm"]
    },
    ("product", "am"): {
        "skills": ["product roadmap", "design thinking", "user stories", "a/b testing", "backlog grooming", "agile sprint", "requirement gathering", "feature planning", "customer feedback", "go-live mgmt"],
        "tools": ["jira", "figma", "trello", "notion", "miro", "postman", "slack", "google analytics", "excel", "ppt"],
        "domain": ["ux", "product mgmt", "saas", "agile delivery", "startup product", "platform strategy", "mvp", "user research", "customer journey", "market fit"],
        "education": ["btech", "mba", "bca", "msc cs", "pg diploma in product", "mba tech", "mba pm", "bdes", "mba it", "ba econ"]
    },
    ("compliance", "avp"): {
        "skills": ["audit", "compliance reporting", "risk control", "policy mgmt", "internal control", "ethics mgmt", "process validation", "incident tracking", "gap analysis", "compliance training"],
        "tools": ["compliance tracker", "ms excel", "word", "legal tech", "audit software", "sap grc", "regulatory platform", "email", "ppt", "jira"],
        "domain": ["regulatory compliance", "legal operations", "internal audit", "statutory norms", "financial governance", "corporate compliance", "contract mgmt", "risk assurance", "company law", "gdpr"],
        "education": ["llb", "mba", "ca", "cs", "mcom", "pg diploma compliance", "mba audit", "bcom", "mba legal", "llm"]
    },
    ("strategy & analytics", "manager"): {
        "skills": ["forecasting", "competitive analysis", "financial modeling", "kpi tracking", "business cases", "sql", "python", "hypothesis testing", "dashboarding", "scenario planning"],
        "tools": ["powerbi", "excel", "sql", "tableau", "python", "google sheets", "notion", "ppt", "lookerstudio", "qlik"],
        "domain": ["business strategy", "market intelligence", "data analytics", "corporate planning", "operational analytics", "growth strategy", "financial planning", "insight generation", "roi analysis", "benchmarking"],
        "education": ["mba", "statistics", "btech", "ba economics", "msc math", "pgdm", "mba analytics", "mcom", "mba strategy", "ca"]
    },
    ("claims, inbound & onboarding", "executive"): {
        "skills": ["claims registration", "customer query resolution", "inbound calling", "policy validation", "document collection", "onboarding call", "email handling", "ticket mgmt", "crm entry", "claim tracking"],
        "tools": ["crm", "dialer", "email", "excel", "policy admin system", "ticketing system", "sms platform", "google forms", "call recorder", "zendesk"],
        "domain": ["insurance process", "customer onboarding", "claims processing", "call center", "policy servicing", "inbound sales", "claims documentation", "support ops", "life insurance", "health insurance"],
        "education": ["graduate", "bcom", "bba", "ba", "pg diploma insurance", "mba insurance", "certification irda", "diploma ops", "msc insurance", "bsc"]
    },
    ("admin", "executive"): {
        "skills": ["facility mgmt", "vendor coordination", "asset tracking", "stationery procurement", "transport mgmt", "security liaison", "office maintenance", "staff logistics", "id card issuing", "compliance logs"],
        "tools": ["excel", "biometrics", "sap", "asset software", "vendor system", "email", "attendance tool", "ppt", "google drive", "security mgmt"],
        "domain": ["admin ops", "facility services", "logistics", "vendor mgmt", "infrastructure", "office support", "security compliance", "pantry mgmt", "site mgmt", "building mgmt"],
        "education": ["graduate", "bcom", "diploma admin", "bba", "ba", "bsc", "mba operations", "msc logistics", "bms", "pg diploma mgmt"]
    },
    ("founder's office", "avp"): {
        "skills": ["business research", "board presentation", "cx support", "special projects", "org structure", "benchmarking", "strategic comms", "model building", "founder collaboration", "financial analysis"],
        "tools": ["ppt", "excel", "powerbi", "google sheets", "notion", "miro", "word", "asana", "dashboards", "confluence"],
        "domain": ["corporate strategy", "cx office", "high impact roles", "investment support", "founder engagement", "biz transformation", "planning", "team synergy", "adhoc projects", "competitive intelligence"],
        "education": ["mba", "btech", "ba eco", "bba", "pgdm", "mba strat", "mba finance", "msc", "mba ib", "mba innovation"]
    },
    ("customer excellence", "manager"): {
        "skills": ["feedback mgmt", "nps tracking", "root cause analysis", "customer journey", "service delivery", "crm escalation", "customer sat", "email reply mgmt", "ticket resolution", "quality audits"],
        "tools": ["zendesk", "crm", "freshdesk", "google forms", "call center tech", "email tools", "dashboard", "excel", "ppt", "confluence"],
        "domain": ["cx", "service quality", "issue resolution", "escalation handling", "retention", "customer support", "process improvement", "cx strategy", "client mgmt", "csat"],
        "education": ["mba", "bba", "graduate", "pgdm", "msc quality", "mba ops", "msc analytics", "bcom", "bms", "mba marketing"]
    },
    ("learning & development", "am"): {
        "skills": ["training delivery", "learning need analysis", "e-learning", "program facilitation", "capability building", "content creation", "training calendar", "feedback analysis", "coaching", "talent development"],
        "tools": ["lms", "ppt", "excel", "google classroom", "zoom", "teams", "slido", "google forms", "moodle", "email"],
        "domain": ["capability building", "training ops", "organizational development", "employee engagement", "hrd", "skill enhancement", "leadership training", "upskilling", "learning design", "behavioral training"],
        "education": ["pgdm", "mba hr", "ma psychology", "bba", "msc hr", "mba learning", "bcom", "ba education", "b.ed", "mba"]
    },
    ("reinsurance", "manager"): {
        "skills": ["underwriting", "reinsurance treaties", "loss ratio analysis", "risk assessment", "quota share", "facultative treaty", "pricing models", "risk aggregation", "retention management", "claims payout"],
        "tools": ["excel", "underwriting software", "reinsurance platform", "crm", "analytics suite", "sql", "risk tool", "ppt", "sas", "email"],
        "domain": ["risk underwriting", "insurance", "reinsurance", "actuarial", "policy structuring", "insurance finance", "retrocession", "treaty mgmt", "claims mgmt", "global risk"],
        "education": ["actuarial science", "mba insurance", "mba", "ca", "pg diploma insurance", "bcom", "llb", "msc statistics", "mba finance", "ba eco"]
    },
    ("oem & dealership", "dm"): {
        "skills": ["dealer onboarding", "inventory tracking", "sales mgmt", "pricing", "billing coordination", "stock transfer", "partner mgmt", "dispatch", "lead mgmt", "territory planning"],
        "tools": ["dealer mgmt system", "erp", "excel", "crm", "sap", "email", "ppt", "salesforce", "inventory tool", "dashboards"],
        "domain": ["automotive", "distribution", "retail operations", "channel partner", "stock allocation", "dealer mgmt", "b2b sales", "supply chain", "vehicle ops", "trade finance"],
        "education": ["mba ops", "btech", "mba", "pgdm", "bba", "bcom", "mba supply", "bms", "mba marketing", "msc"]
    },
    ("renewal", "manager"): {
        "skills": ["retention", "policy renewal", "customer follow-up", "payment collection", "lapsed conversion", "win-back", "reminder calls", "nps", "crm updates", "premium calculation"],
        "tools": ["crm", "excel", "dialer", "email", "policy admin system", "google sheets", "sms tool", "powerbi", "ppt", "telephony"],
        "domain": ["renewals", "customer lifecycle", "policy mgmt", "health insurance", "term insurance", "insurance sales", "customer retention", "follow-up ops", "conversion funnel", "cx"],
        "education": ["graduate", "bcom", "bba", "mba insurance", "pg diploma insurance", "mba", "msc", "bsc", "ba", "bms"]
    },
    ("partnership", "sm"): {
        "skills": ["channel mgmt", "partner acquisition", "bd", "contract negotiation", "account mgmt", "crm mgmt", "partner training", "forecasting", "pipeline mgmt", "relationship mgmt"],
        "tools": ["crm", "excel", "ppt", "hubspot", "email", "pipeline software", "microsoft teams", "notion", "zoho", "reporting dashboards"],
        "domain": ["partnerships", "alliances", "bd", "sales strategy", "distribution", "saas channels", "account mgmt", "key accounts", "relationship mgmt", "vendor mgmt"],
        "education": ["mba", "bcom", "bba", "mba marketing", "mba sales", "pgdm", "mba bd", "mba strat", "btech", "msc"]
    },
    ("procurement", "am"): {
        "skills": ["vendor mgmt", "po creation", "negotiation", "sourcing", "cost reduction", "rfq", "contract mgmt", "grn mgmt", "inventory mgmt", "order tracking"],
        "tools": ["sap", "excel", "tally", "oracle procurement", "email", "rfq tool", "ppt", "erp", "google sheets", "vendor portal"],
        "domain": ["procurement", "supply chain", "vendor ops", "logistics", "material mgmt", "inventory", "purchasing", "warehousing", "finance", "admin ops"],
        "education": ["btech", "mba", "mba ops", "bcom", "pg diploma supply", "msc logistics", "mba procurement", "ba", "bms", "mba scm"]
    },
    ("product", "director"): {
        "skills": ["product vision", "go-to-market", "cross-functional leadership", "product roadmap", "market research", "kpi mgmt", "team mgmt", "growth metrics", "strategic planning", "portfolio mgmt"],
        "tools": ["figma", "jira", "miro", "confluence", "ppt", "excel", "powerbi", "notion", "trello", "productboard"],
        "domain": ["product strategy", "platform mgmt", "product lifecycle", "customer centric design", "saas product", "enterprise product", "mvp", "innovation mgmt", "agile", "market fit"],
        "education": ["mba", "btech", "mba pm", "mba strategy", "msc product", "mba tech", "ba", "bdes", "mba marketing", "mba it"]
    },
    ("insurer relation", "manager"): {
        "skills": ["insurer onboarding", "pricing negotiation", "sla management", "relationship handling", "claim coordination", "renewal support", "data exchange", "regulatory liaison", "underwriting support", "product filing"],
        "tools": ["crm", "excel", "policy admin system", "email", "ppt", "reporting tools", "ms office", "google sheets", "jira", "dashboard"],
        "domain": ["insurance operations", "insurer management", "underwriting", "network management", "insurance partners", "contract terms", "policy servicing", "alliance management", "health insurance", "motor insurance"],
        "education": ["mba", "bcom", "bba", "mba insurance", "pg diploma insurance", "bms", "graduate", "mba marketing", "llb", "msc"]
    },
    ("founder's office", "manager"): {
        "skills": ["business analysis", "special projects", "founder support", "investor deck", "competitor analysis", "data synthesis", "market scoping", "board presentation", "project tracking", "kpi ownership"],
        "tools": ["ppt", "excel", "google sheets", "notion", "miro", "powerbi", "figma", "email", "word", "airtable"],
        "domain": ["strategy", "special initiatives", "new verticals", "growth ops", "business performance", "startup ops", "vc communication", "investor relations", "metrics mgmt", "research"],
        "education": ["mba", "btech", "mba strategy", "mba marketing", "mba finance", "bba", "pgdm", "ba economics", "ca", "msc"]
    },
    ("claims, inbound & onboarding", "am"): {
        "skills": ["claims coordination", "onboarding experience", "email handling", "tpa mgmt", "policy updates", "customer support", "document verification", "claim escalation", "payment follow-up", "mis tracking"],
        "tools": ["crm", "email client", "excel", "policy software", "ticketing tool", "ivr tool", "tally", "google forms", "shared drive", "sap"],
        "domain": ["insurance process", "claims mgmt", "customer onboarding", "policy servicing", "support ops", "insurance support", "medical claims", "motor claims", "tpa coordination", "service delivery"],
        "education": ["graduate", "bcom", "bba", "mba", "mba insurance", "pg diploma", "msc", "llb", "ba", "bsc"]
    },
    ("customer excellence", "avp"): {
        "skills": ["cx strategy", "escalation resolution", "service design", "voice of customer", "cx automation", "feedback loop", "nps strategy", "net promoter improvement", "ops efficiency", "team management"],
        "tools": ["zendesk", "crm", "email", "powerbi", "excel", "dashboard tool", "slack", "jira", "ppt", "survey tools"],
        "domain": ["customer experience", "service quality", "cx governance", "support ops", "customer journey", "cx metrics", "call center", "nps", "retention", "customer loyalty"],
        "education": ["mba", "btech", "mba operations", "mba marketing", "pgdm", "bba", "msc", "ca", "bcom", "ba"]
    },
    ("strategy & analytics", "avp"): {
        "skills": ["financial modeling", "growth strategy", "competitive benchmarking", "forecasting", "dashboard creation", "business case development", "kpi alignment", "revenue modeling", "cohort analysis", "board level insights"],
        "tools": ["powerbi", "tableau", "excel", "sql", "ppt", "notion", "airtable", "python", "r", "google sheets"],
        "domain": ["corporate strategy", "analytics", "business intelligence", "revenue strategy", "go-to-market", "market scoping", "performance mgmt", "financial planning", "okrs", "data storytelling"],
        "education": ["mba", "mba finance", "mba analytics", "btech", "ca", "msc statistics", "mba strategy", "bba", "ba economics", "pgdm"]
    }


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

    # Phrase-aware matching
    all_phrases = set()
    for role in ROLE_KEYWORDS.values():
        for field in ["skills", "tools", "domain", "education"]:
            all_phrases.update(role.get(field, []))

    # Flatten synonyms too
    for k, syns in SYNONYMS.items():
        all_phrases.add(k)
        all_phrases.update(syns)

    matched_phrases = match_phrases_from_text(text, all_phrases)

    combined = list(set(filtered + matched_phrases))

    return {
        "skills": combined,
        "tools": combined,
        "domain": combined,
        "education": combined
    }
