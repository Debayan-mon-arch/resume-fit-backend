import fitz  # PyMuPDF
from docx import Document
import re

# --- Main unified function ---
def extract_text(file):
    try:
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            file.stream.seek(0)
            return extract_relevant_text_from_pdf(file).replace("\n", " ").strip().lower()
        elif filename.endswith(".docx"):
            file.stream.seek(0)
            return extract_relevant_text_from_docx(file).replace("\n", " ").strip().lower()
        else:
            return file.read().decode("utf-8", errors="ignore").replace("\n", " ").strip().lower()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# --- Trim to relevant JD content ---
def trim_to_relevant_section(text):
    triggers = [
        "role title", "roles and responsibilities", "responsibilities",
        "job description", "about the role", "role overview",
        "key responsibilities", "key skills and qualifications",
        "educational qualifications", "experience"
    ]
    lower_text = text.lower()
    for trigger in triggers:
        idx = lower_text.find(trigger)
        if idx != -1:
            return text[idx:]
    return text  # fallback if no match

# --- PDF ---
def extract_relevant_text_from_pdf(file):
    text = ""
    doc = fitz.open("pdf", file.read())
    for page in doc:
        text += page.get_text()
    doc.close()
    return trim_to_relevant_section(text)

# --- DOCX ---
def extract_relevant_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return trim_to_relevant_section(text)

# --- Synonym Bank ---
SYNONYMS = {
    "python": ["py", "python3", "scripting", "backend scripting"],
    "git": ["gitlab", "github", "version control", "git system"],
    "docker": ["containers", "containerization", "docker engine", "dockerized app"],
    "cloud": ["aws", "azure", "gcp", "cloud infra", "cloud architecture", "cloud environment", "cloud platform", "saas hosting"],
    "recruitment": ["talent acquisition", "hiring", "staffing", "headhunting", "candidate sourcing", "resourcing", "talent mapping", "recruiting", "manpower planning"],
    "employee relations": ["grievance", "hrbp", "employee engagement", "people mgmt", "conflict resolution", "employee satisfaction", "hr connect", "internal resolution"],
    "branding": ["brand", "identity", "positioning", "rebranding", "brand management", "employer branding", "brand image", "visual identity"],
    "content creation": ["copywriting", "social content", "reels", "posts", "creative writing", "content development", "media scripting", "digital copy"],
    "campaign execution": ["campaign mgmt", "brand activation", "ad launch", "promotion", "event rollout", "campaign planning", "campaign delivery"],
    "compliance": ["risk", "regulations", "audit", "regulatory", "legal", "policy adherence", "standard operating procedures", "statutory"],
    "strategy": ["strategic", "planning", "roadmap", "vision", "go-to-market", "growth planning", "market strategy", "tactical alignment"],
    "analytics": ["data", "dashboards", "metrics", "visualization", "reporting", "insight generation", "statistical analysis", "trend analysis"],
    "finance": ["accounting", "p&l", "budgeting", "forecasting", "cost control", "financial modeling", "fund flow", "capital expenditure"],
    "sales": ["targets", "pipeline", "conversion", "revenue", "upselling", "leads", "client acquisition", "quota achievement"],
    "hr": ["onboarding", "exit", "retention", "training", "employee lifecycle", "hr operations", "personnel management", "induction"],
    "technology": ["devops", "infra", "architecture", "it systems", "backend", "systems design", "technical stack", "infrastructure support"],
    "b2b": ["enterprise", "partner", "channel sales", "corporate sales", "institutional sales", "business clients", "account-based marketing"],
    "b2c": ["consumer", "customer", "d2c", "retail sales", "end-user", "direct customer", "mass audience"],
    "supply": ["logistics", "inventory", "fulfillment", "procurement", "dispatch", "distribution", "warehouse", "supply chain"],
    "renewal": ["retention", "follow-up", "lifecycle", "policy renewal", "subscription renewal", "renewal tracking", "customer callbacks"],
    "marketing": ["seo", "sem", "campaign", "adwords", "brand mgmt", "digital marketing", "performance marketing", "advertising"],
    "product": ["ux", "feature", "roadmap", "requirement gathering", "release planning", "product design", "go-to-market", "product vision"],
    "training": ["learning", "l&d", "skills building", "e-learning", "training delivery", "capability building", "coaching", "facilitation"],
    "crm": ["salesforce", "zoho", "hubspot", "lead mgmt", "customer database", "crm tools", "crm updates", "client tracking"],
    "customer service": ["support", "queries", "client care", "inbound calls", "customer experience", "issue resolution", "call center ops"],
    "negotiation": ["deal closure", "pricing discussion", "bargaining", "contract finalization", "commercial agreement", "cost negotiation"],
    "lead generation": ["prospecting", "cold calling", "inbound leads", "outreach", "lead funnel", "client acquisition", "lead nurturing"],
    "telecalling": ["calling", "voice process", "phone sales", "dialing", "call handling", "inbound calls", "telemarketing"],
    "excel": ["spreadsheets", "formulas", "pivot tables", "vlookup", "excel modeling", "data sorting", "macros", "dashboards"],
    "powerpoint": ["presentations", "slides", "ppt", "pitch decks", "slide design", "storyboarding", "slide creation"],
    "erp": ["sap", "oracle", "ms dynamics", "netsuite", "erp system", "enterprise resource planning", "erp tools"],
    "legal": ["contract", "litigation", "compliance", "corporate law", "legal policy", "case law", "regulatory", "legal documentation"],
    "vendor management": ["supplier mgmt", "third party", "procurement", "vendor onboarding", "vendor coordination", "supplier relations"],
    "forecasting": ["prediction", "modeling", "trend analysis", "sales forecast", "budgeting forecast", "financial outlook"],
    "insurance": ["policy", "claim", "premium", "underwriting", "insurance ops", "insurance sales", "insurance process"],
    "cx": ["customer experience", "nps", "feedback", "csat", "service quality", "customer satisfaction", "experience mgmt"],
    "lms": ["learning system", "elearning", "online courses", "learning portal", "virtual training platform"],
    "dashboarding": ["visualization", "reporting", "kpi tracker", "bi dashboard", "performance metrics"],
    "automation": ["bots", "scripts", "workflow tools", "rpa", "automated process", "task automation"],
    "sql": ["structured query", "database query", "postgres", "mysql", "pl/sql", "data extraction"],
    "presentation": ["slides", "decks", "ppt", "presenting", "client deck", "visual slides"],
    "contract": ["agreement", "mou", "legal document", "service agreement", "commercial contract"],
    "coordination": ["scheduling", "follow-ups", "team sync", "meeting coordination", "stakeholder updates"],
    "operations": ["ops", "daily mgmt", "service delivery", "backend ops", "operations support"],
    "client": ["customer", "stakeholder", "partner", "account", "client interaction", "client servicing"],
    "admin": ["facilities", "office mgmt", "support staff", "vendor liaison", "administrative ops"],
    "research": ["analysis", "insights", "study", "evaluation", "market research", "desk research"],
    "performance marketing": ["paid ads", "cpc", "ppc", "google ads", "meta ads", "facebook ads", "digital acquisition"],
    "graphic design": ["visuals", "illustrations", "branding", "canva", "creative assets", "graphic tools"],
    "email marketing": ["mailchimp", "newsletter", "campaign", "cold emails", "email engagement"],
    "field sales": ["on-ground", "door-to-door", "feet-on-street", "field visits", "territory sales"],
    "internal audit": ["compliance check", "risk control", "process audit", "financial audit", "internal checks"],
    "training delivery": ["facilitation", "classroom", "skill transfer", "virtual training", "program facilitation"],
    "claims": ["reimbursements", "settlements", "processing", "claim handling", "claim approval"],
    "policy": ["insurance", "coverage", "benefits", "policy administration", "policy management"],
    "ecommerce": ["online retail", "shopping", "cart", "product listing", "checkout process"],
    "project mgmt": ["scrum", "agile", "kanban", "milestones", "timeline mgmt", "project execution"],
    "support": ["service desk", "helpdesk", "ticket", "user support", "support function"],
    "leadership": ["people mgmt", "team lead", "supervisor", "managerial", "team handling"],
    "documentation": ["sop", "manual", "handbook", "process doc", "training material"],
    "planning": ["roadmap", "timeline", "blueprint", "action plan", "execution planning"],
    "pricing": ["costing", "valuation", "quote", "pricing strategy", "price modeling"],
    "growth": ["scaling", "expansion", "go-to-market", "growth hacking", "growth strategy"],
    "ux": ["ui", "user experience", "interaction design", "usability", "user interface"],
    "revenue": ["income", "sales", "billing", "earning", "monetization"],
    "strategy": ["approach", "tactics", "plan", "game plan", "execution strategy"],
    "business development": ["bd", "sales", "client acquisition", "deal sourcing", "new business"],
    "founder support": ["ceo office", "special projects", "executive support", "founder alignment", "key initiatives"],
    "comms": ["communication", "emails", "presentations", "internal comms", "external comms"],
    "social media": ["facebook", "instagram", "linkedin", "twitter", "social engagement"],
    "inventory": ["stock", "goods", "items", "inventory tracking", "stock control"],
    "campaign": ["promo", "advertising", "outreach", "campaign strategy", "ad campaign"],
     "sourcing": ["talent sourcing", "headhunting", "candidate search", "boolean search", "cv mining"],
    "talent management": ["workforce planning", "succession planning", "capability building", "talent pipeline"],
    "interviewing": ["interviewing candidates", "screening", "assessment", "technical interview", "hr round"],
    "employee engagement": ["motivation", "engagement programs", "retention", "culture building", "pulse survey"],
    "payroll": ["salary processing", "payroll compliance", "pf/esi", "payroll software", "monthly salary"],
    "compliance management": ["labor law", "hr compliance", "statutory compliance", "regulatory checks"],
    "organizational development": ["org design", "change mgmt", "transformation", "org structuring", "od initiatives"],
    "attrition": ["churn", "turnover", "resignation", "exit analysis", "attrition management"],
    "data analytics": ["excel analysis", "google sheets", "data slicing", "hr dashboard", "pivot charts"],
    "performance appraisal": ["pa system", "annual review", "bell curve", "kpi tracking", "mid-year review"],
    "recruitment analytics": ["funnel metrics", "sourcing conversion", "turnaround time", "offer ratio", "hire quality"],
    "succession planning": ["backup planning", "next role mapping", "talent bench", "critical role planning"],
    "job description": ["jd writing", "role profiling", "job specs", "responsibility drafting"],
    "evp": ["employer value proposition", "employer brand", "employee branding", "value prop"],
    "culture": ["org culture", "employee behaviour", "value alignment", "culture fit", "core values"],
    "team management": ["people mgmt", "mentoring", "delegation", "performance mgmt", "coaching"],
    "grievance": ["employee complaint", "escalation", "issue resolution", "hr helpdesk", "dispute mgmt"],
    "hrms": ["workday", "darwinbox", "zoho people", "greythr", "bamboohr", "keka"],
    "offer mgmt": ["offer letters", "negotiation", "joining confirmation", "ctc structuring"],
    "exit mgmt": ["exit interviews", "fnf", "knowledge transfer", "clearances", "offboarding"],
    "comp & ben": ["compensation", "rewards", "benefits", "variable pay", "incentive plan"],
    "leadership hiring": ["cx hiring", "mid-senior roles", "director hiring", "avp hiring", "exec hiring"],
    "startup hiring": ["hypergrowth hiring", "tech recruitment", "zero to one team", "founder alignment"],
    "strategic hiring": ["future roles", "talent strategy", "planned recruitment", "skills map"],
    "talent acquisition": ["recruitment", "hiring", "staffing", "headhunting", "acquisition team"],
    "stakeholder management": ["hiring manager mgmt", "recruiter alignment", "meeting alignment", "update sharing"],
    "onboarding": ["joining", "induction", "orientation", "candidate experience", "welcome kit"],
    "esops": ["employee stock", "stock options", "esop policy", "vesting schedule"],
    "background verification": ["bgv", "reference check", "third party screening", "compliance clearance"],
    "internal mobility": ["role switch", "cross-functional move", "career pathing", "talent redeployment"],
    "diversity hiring": ["women hiring", "inclusion", "diverse talent", "inclusive hiring"],
    "hiring targets": ["monthly goals", "target v/s achieved", "funnel mgmt", "headcount plan"],
    "college hiring": ["campus recruitment", "placement drives", "intern hiring", "graduate program"],
    "lateral hiring": ["experienced hires", "mid-career", "industry hire", "non-freshers"],
    "mass hiring": ["bulk hiring", "walk-ins", "drive mgmt", "event-based hiring"],
    "vendor mgmt": ["consultant mgmt", "third-party tie-up", "vendor contracts", "agency hiring"],
    "talent pipeline": ["candidate pool", "backup resources", "potential hires", "pipeline building"],
    "job boards": ["naukri", "indeed", "linkedin", "shine", "timesjobs"],
    "boolean search": ["advanced search", "sourcing logic", "operator query", "string-based search"],
    "headhunting": ["active search", "targeted reachout", "executive search", "senior talent sourcing"],
    "walk-in drive": ["walk-in recruitment", "drive event", "mass hiring event", "offline hiring"],
    "contract hiring": ["temp hiring", "project-based hiring", "consultant hiring", "short-term contract"],
    "referral hiring": ["employee referrals", "referral bonus", "referral drive", "internal leads"],
    "screening": ["resume review", "cv shortlisting", "profile filtering", "first-level assessment"],
    "interview scheduling": ["calendar sync", "candidate invite", "interview setup", "panel coordination"],
    "recruitment dashboard": ["hiring report", "kpi dashboard", "conversion charts", "performance metrics"],
    "candidate experience": ["candidate journey", "feedback mechanism", "experience mgmt", "joining feedback"],
    "hiring forecast": ["recruitment projection", "manpower plan", "future hiring", "attrition backfill"],
    "requisition": ["job requisition", "hiring request", "req form", "open role"],
    "approval flow": ["offer approval", "budget signoff", "role validation", "headcount clearance"],
    "talent mapping": ["market mapping", "competitor hiring", "talent intelligence", "skill benchmarking"],
    "internal hiring": ["promotion", "internal move", "role switch", "talent mobility"],
    "panel calibration": ["interviewer alignment", "evaluation sync", "rating matrix", "interview prep"],
    "job architecture": ["role leveling", "band structure", "org charting", "grade mapping"],
    "benchmarking": ["industry comparison", "market data", "salary benchmarks", "role parity"],
    "KRA setting": ["goal setting", "objective alignment", "KPI design", "performance goal"],
    "compensation revision": ["ctc change", "salary update", "pay hike", "annual increment"],
    "org design": ["structure change", "org restructuring", "hierarchy plan", "team redesign"],
    "talent audit": ["skills gap", "headcount audit", "role redundancy", "talent review"],
    "workforce analytics": ["people data", "attrition analytics", "hiring trends", "talent scorecard"],
    "leadership development": ["hi-po programs", "succession pipeline", "executive grooming", "future leaders"],
    "culture audit": ["engagement audit", "culture heatmap", "pulse insights", "value alignment"],
    "talent review": ["performance grid", "9-box", "potential mapping", "talent visibility"],
    "competency framework": ["behavioral traits", "skill matrix", "role competency", "leadership traits"],
    "performance tracking": ["KRA tracking", "goal achievement", "scorecard mgmt", "review tracker"],
    "talent council": ["hr council", "review panel", "succession board", "leadership review"],
}

# --- Role Keyword Mapping (Dept, Level) aligned with frontend ---
ROLE_KEYWORDS = {
    ("human resources", "am"): {
        "skills": [
            "recruitment", "talent acquisition", "employee relations", "onboarding", "exit interviews",
            "performance management", "succession planning", "grievance handling", "organizational development",
            "hr audits", "hr analytics", "employee engagement", "internal communication", "conflict resolution",
            "workforce planning", "change management", "learning and development", "retention strategy",
            "policy creation", "benefits administration", "end-to-end hiring", "hiring", "Spearheaded", "onboarding", "key hiring metrics", "cost of hiring", "TAT", "source utilization"
        ],
        "tools": [
            "excel", "powerpoint", "workday", "successfactors", "greytHR", "zoho people", "darwinbox", "bambooHR",
            "keka", "linkedin recruiter", "naukri RMS", "greenhouse", "sap hr", "oracle hcm", "ms office",
            "google workspace", "jira", "confluence", "tableau", "powerbi"
        ],
        "domain": [
            "people operations", "strategic hrm", "industrial relations", "labour law compliance",
            "diversity and inclusion", "employee lifecycle", "talent development", "change leadership",
            "hr transformation", "hr digitalization", "employee retention", "hr compliance", "work culture",
            "hr business partnering", "performance systems", "organizational structure", "capability building",
            "leadership development", "hr technology", "remote workforce strategy", "B2B", "B2C"
        ],
        "education": [
            "mba hr", "pgdm hr", "bba hr", "ma psychology", "msw", "ba sociology", "mba ob", "mba l&d",
            "mba ir", "bcom hr", "pg diploma in hr", "certification in labor laws", "psychology degree",
            "human capital management diploma", "mba in organizational behavior", "msc in hr analytics",
            "mba people management", "mba in leadership", "executive mba hr", "bachelor in industrial psychology"
        ]
    },
    ("marketing", "manager"): {
        "skills": [
            "branding", "seo", "sem", "performance marketing", "market research", "go-to-market",
            "demand generation", "email marketing", "content strategy", "influencer marketing",
            "media buying", "customer segmentation", "brand activation", "event marketing",
            "growth marketing", "retention marketing", "lead generation", "product marketing",
            "marketing automation", "multichannel marketing"
        ],
        "tools": [
            "google ads", "meta business suite", "canva", "mailchimp", "hubspot", "google analytics",
            "ahrefs", "semrush", "figma", "hootsuite", "notion", "slack", "buffer", "crm", "adobe creative cloud",
            "clevertap", "moengage", "hotjar", "microsoft excel", "ppt"
        ],
        "domain": [
            "digital marketing", "brand management", "media planning", "consumer behavior", "content marketing",
            "btl/atl marketing", "public relations", "community building", "retail marketing", "omnichannel strategy",
            "customer lifecycle", "ecommerce marketing", "performance campaigns", "brand storytelling",
            "social listening", "marketing funnels", "market penetration", "regional marketing",
            "competitive positioning", "marketing compliance"
        ],
        "education": [
            "mba marketing", "pgdm marketing", "bba marketing", "mass communication", "advertising diploma",
            "bmm", "ba communication", "mba digital marketing", "certified digital marketer", "bms",
            "mba brand management", "mba media", "pg in brand communications", "diploma in mass media",
            "mba marcom", "bcom marketing", "mba in international marketing", "mba in strategic marketing",
            "executive mba marketing", "mba in consumer insights"
        ]
    },
    ("technology", "senior executive"): {
        "skills": [
            "python", "java", "system design", "data structures", "oop", "rest apis", "agile", "testing",
            "debugging", "scalability", "microservices", "ci/cd", "unit testing", "integration testing",
            "software architecture", "backend development", "frontend frameworks", "containerization",
            "cloud native design", "api integration"
        ],
        "tools": [
            "git", "docker", "kubernetes", "vscode", "jenkins", "intellij", "postman", "jira", "confluence",
            "linux", "aws", "azure", "gcp", "terraform", "ansible", "datadog", "grafana", "splunk", "helm", "gitlab"
        ],
        "domain": [
            "backend engineering", "frontend development", "cloud systems", "distributed systems", "devops",
            "infra ops", "database management", "app security", "api gateway", "platform engineering",
            "site reliability engineering", "fullstack development", "saas platforms", "web services",
            "container orchestration", "system performance", "server-side architecture", "infrastructure as code",
            "cloud architecture", "api design"
        ],
        "education": [
            "btech", "mtech", "b.e", "b.sc computer science", "mca", "bca", "btech it", "btech cse",
            "msc cs", "pg diploma in cs", "certificate in fullstack dev", "cloud architect certification",
            "devops engineering cert", "aws solutions architect", "azure developer cert", "google cloud cert",
            "diploma in software engg", "mba it", "msc data science"
        ]
    },
    ("finance", "manager"): {
        "skills": [
            "budgeting", "forecasting", "variance analysis", "financial modeling", "fund flow", "p&l",
            "accounting", "cash flow", "roi analysis", "payroll management", "cost optimization",
            "financial reporting", "internal audit", "risk management", "statutory compliance",
            "consolidation", "capex planning", "taxation", "working capital management", "regulatory filing"
        ],
        "tools": [
            "tally", "excel", "quickbooks", "zoho books", "sap fico", "oracle finance", "powerbi", "erp",
            "netsuite", "busy accounting", "ms office", "marg erp", "intuit", "xero", "workiva", "blackline",
            "finly", "cleartax", "zoho analytics", "spreadsheet modeling tools"
        ],
        "domain": [
            "corporate finance", "accounting & audit", "financial control", "statutory compliance", "taxation",
            "treasury", "internal audit", "budget planning", "working capital mgmt", "cost control",
            "management accounting", "financial planning & analysis", "regulatory finance", "investor reporting",
            "credit risk", "banking & nbfc", "startup finance", "mergers and acquisitions", "fp&a",
            "financial governance"
        ],
        "education": [
            "ca", "mba finance", "cfa", "icwa", "bcom", "mcom", "cs", "pg diploma in finance", "bba finance",
            "acca", "financial modeling cert", "accounting diploma", "advanced excel finance", "mba accounting",
            "llb tax laws", "mba taxation", "mba audit", "b.sc finance", "mba investment banking", "mba analytics"
        ]
    },
    ("b2b", "senior executive"): {
        "skills": [
            "negotiation", "partner acquisition", "sales pipeline", "lead qualification", "cold calling",
            "crm hygiene", "proposal writing", "demo pitching", "cross-sell", "key account management",
            "channel development", "enterprise sales", "contract negotiation", "field sales", "target chasing",
            "account-based marketing", "pre-sales", "b2b closing", "relationship management", "conversion strategy"
        ],
        "tools": [
            "excel", "salesforce", "zoho crm", "hubspot", "outreach", "linkedin sales navigator", "ppt", "aircall",
            "mailmerge", "whatsapp web", "microsoft teams", "google sheets", "pipedrive", "freshsales", "lead squared",
            "gong.io", "insightly", "callhippo", "crm analytics", "lusha"
        ],
        "domain": [
            "enterprise sales", "channel sales", "partnership onboarding", "account-based marketing",
            "reseller management", "pre-sales", "post-sales support", "b2b marketing", "inside sales",
            "solution selling", "logistics partnerships", "corporate accounts", "hardware/software sales",
            "consultative selling", "large account mgmt", "industrial sales", "service sales", "edtech b2b",
            "manufacturing sales", "btob tech sales"
        ],
        "education": [
            "mba sales", "bcom", "mba marketing", "pgdm sales", "bba", "ba economics", "mba b2b", "bsc", "mba ib",
            "mba comm", "mba international business", "mba strategic sales", "mba enterprise sales", "mba smarketing",
            "diploma in marketing", "pg sales mgmt", "cert sales mgmt", "mba consulting", "mba b2b marketing"
        ]
    },
    ("b2c", "executive"): {
        "skills": [
            "telecalling", "lead conversion", "upselling", "objection handling", "product pitching", "follow-ups",
            "customer onboarding", "demo scheduling", "sales scripts", "crm entry", "retention calling", "closing",
            "need analysis", "cross-sell", "service query resolution", "soft skills", "inbound support", "rebuttals",
            "sales follow-through", "telephonic persuasion"
        ],
        "tools": [
            "dialer", "leadsquared", "zoho crm", "excel", "call recorder", "outlook", "freshdesk", "aircall",
            "salesforce", "sms blast", "google sheets", "voice logger", "asterisk", "avaya", "ringcentral",
            "chatdesk", "ticketing system", "ivr systems", "whatsapp crm", "telephony dashboard"
        ],
        "domain": [
            "inbound sales", "tele-sales", "consumer onboarding", "support transition", "b2c funnel", "retention",
            "direct sales", "field conversion", "d2c", "post-sale services", "customer experience", "support process",
            "insurance sales", "loan sales", "product subscriptions", "health insurance sales", "term plans",
            "credit card sales", "travel package sales", "real estate lead conversion"
        ],
        "education": [
            "graduate", "bba", "ba", "bcom", "bca", "pg diploma", "mba", "diploma in sales", "mass comm", "bmm",
            "certificate in sales communication", "telecalling diploma", "call center cert", "bsc", "mba d2c",
            "customer service diploma", "bachelor’s degree", "retail diploma", "pg in service marketing"
        ]
    },
    ("product", "am"): {
        "skills": [
            "product roadmap", "design thinking", "user stories", "a/b testing", "backlog grooming", "agile sprint",
            "requirement gathering", "feature planning", "customer feedback", "go-live mgmt", "wireframing",
            "product lifecycle", "competitor analysis", "growth hacking", "product strategy", "persona definition",
            "mvp planning", "cross-functional coordination", "usability testing", "kanban"
        ],
        "tools": [
            "jira", "figma", "trello", "notion", "miro", "postman", "slack", "google analytics", "excel", "ppt",
            "clickup", "airtable", "confluence", "firebase", "hotjar", "intercom", "productboard", "draw.io",
            "google data studio", "userpilot"
        ],
        "domain": [
            "ux", "product mgmt", "saas", "agile delivery", "startup product", "platform strategy", "mvp",
            "user research", "customer journey", "market fit", "feature prioritization", "growth product",
            "mobile product", "web product", "enterprise product", "product-led growth", "design sprints",
            "competitive analysis", "roadmapping", "customer development"
        ],
        "education": [
            "btech", "mba", "bca", "msc cs", "pg diploma in product", "mba tech", "mba pm", "bdes", "mba it",
            "ba econ", "product mgmt cert", "cs engineering", "mba innovation", "mba design mgmt", "ux diploma",
            "mba operations", "pgdm product", "ms product innovation", "engineering + mba", "startup product mgmt"
        ]
    },
    ("compliance", "avp"): {
        "skills": [
            "audit", "compliance reporting", "risk control", "policy mgmt", "internal control", "ethics mgmt",
            "process validation", "incident tracking", "gap analysis", "compliance training", "statutory compliance",
            "regulatory mapping", "internal audit", "sox compliance", "quality audit", "document control",
            "safety compliance", "contract vetting", "investigation", "legal risk assessment"
        ],
        "tools": [
            "compliance tracker", "ms excel", "word", "legal tech", "audit software", "sap grc", "regulatory platform",
            "email", "ppt", "jira", "navex global", "logicmanager", "metricstream", "powerbi", "zoho docs",
            "confluence", "google drive", "sharepoint", "qlik", "dashboarding"
        ],
        "domain": [
            "regulatory compliance", "legal operations", "internal audit", "statutory norms", "financial governance",
            "corporate compliance", "contract mgmt", "risk assurance", "company law", "gdpr", "hipaa", "environmental compliance",
            "insurance compliance", "pharma compliance", "iso audits", "internal risk", "policy vetting", "labor law",
            "it compliance", "third-party risk"
        ],
        "education": [
            "llb", "mba", "ca", "cs", "mcom", "pg diploma compliance", "mba audit", "bcom", "mba legal", "llm",
            "iso cert", "risk certification", "cisa", "mba risk", "ca inter", "mba corp law", "diploma law", "pg law",
            "bba law", "compliance diploma"
        ]
    },
    ("strategy & analytics", "manager"): {
        "skills": [
            "forecasting", "competitive analysis", "financial modeling", "kpi tracking", "business cases", "sql",
            "python", "hypothesis testing", "dashboarding", "scenario planning", "cost-benefit analysis",
            "business research", "cohort analysis", "market sizing", "insight generation", "data storytelling",
            "statistical modeling", "segmentation", "predictive analytics", "business intelligence"
        ],
        "tools": [
            "powerbi", "excel", "sql", "tableau", "python", "google sheets", "notion", "ppt", "lookerstudio", "qlik",
            "r", "snowflake", "google analytics", "metabase", "dash", "airtable", "confluence", "jupyter",
            "databricks", "kibana"
        ],
        "domain": [
            "business strategy", "market intelligence", "data analytics", "corporate planning",
            "operational analytics", "growth strategy", "financial planning", "insight generation",
            "roi analysis", "benchmarking", "data science", "customer analytics", "pricing strategy",
            "sales analytics", "investor decks", "revenue strategy", "product analytics", "BI reporting",
            "demand forecasting", "business transformation"
        ],
        "education": [
            "mba", "statistics", "btech", "ba economics", "msc math", "pgdm", "mba analytics", "mcom",
            "mba strategy", "ca", "data science diploma", "pgdm analytics", "mba economics", "msc data science",
            "mba finance", "bba analytics", "cert BI", "mba planning", "mba insight", "mba growth"
        ]
    },
    ("claims, inbound & onboarding", "executive"): {
       "skills": [
            "claims registration", "customer query resolution", "inbound calling", "policy validation",
            "document collection", "onboarding call", "email handling", "ticket mgmt", "crm entry", "claim tracking",
            "claims follow-up", "tpa coordination", "grievance handling", "case resolution", "first-call resolution",
            "call logging", "onboarding coordination", "policy support", "customer verification", "claim status updates"
        ],
        "tools": [
            "crm", "dialer", "email", "excel", "policy admin system", "ticketing system", "sms platform",
            "google forms", "call recorder", "zendesk", "freshdesk", "helpdesk", "sap", "google sheets",
            "outlook", "ivr system", "zoho desk", "internal dashboard", "shared drives", "crm next"
        ],
        "domain": [
            "insurance process", "customer onboarding", "claims processing", "call center", "policy servicing",
            "inbound sales", "claims documentation", "support ops", "life insurance", "health insurance",
            "motor insurance", "customer support", "policy queries", "renewal queries", "medical claims",
            "claim intimation", "call support", "onboarding process", "policy assistance", "ops support"
        ],
        "education": [
            "graduate", "bcom", "bba", "ba", "pg diploma insurance", "mba insurance", "certification irda",
            "diploma ops", "msc insurance", "bsc", "pg customer care", "insurance course", "customer service cert",
            "healthcare mgmt diploma", "policy ops cert", "mba ops", "bms", "msc", "insurance onboarding cert",
            "ba public admin"
        ]
    },
    ("admin", "executive"): {
       "skills": [
            "facility mgmt", "vendor coordination", "asset tracking", "stationery procurement", "transport mgmt",
            "security liaison", "office maintenance", "staff logistics", "id card issuing", "compliance logs",
            "admin operations", "maintenance planning", "vendor follow-up", "utility management", "security pass issuance",
            "front desk mgmt", "canteen ops", "building maintenance", "admin audits", "office supplies tracking"
        ],
        "tools": [
            "excel", "biometrics", "sap", "asset software", "vendor system", "email", "attendance tool", "ppt",
            "google drive", "security mgmt", "facility tracker", "admin portal", "crm", "helpdesk", "id card tool",
            "office mgmt system", "inventory software", "internal mailer", "google forms", "shared folders"
        ],
        "domain": [
            "admin ops", "facility services", "logistics", "vendor mgmt", "infrastructure", "office support",
            "security compliance", "pantry mgmt", "site mgmt", "building mgmt", "office hygiene", "asset mgmt",
            "employee logistics", "canteen mgmt", "office renovation", "admin procurement", "admin maintenance",
            "security tracking", "desk management", "admin compliance"
        ],
        "education": [
            "graduate", "bcom", "diploma admin", "bba", "ba", "bsc", "mba operations", "msc logistics", "bms",
            "pg diploma mgmt", "admin cert", "mba facilities", "infra mgmt cert", "office mgmt diploma",
            "security mgmt course", "msc admin", "diploma in facility", "bba infra", "mba admin ops", "btech civil"
        ]
    },
    ("founder's office", "avp"): {
        "skills": [
            "business research", "board presentation", "cx support", "special projects", "org structure",
            "benchmarking", "strategic comms", "model building", "founder collaboration", "financial analysis",
            "investor relations", "market scoping", "business review", "initiative mgmt", "founder decks",
            "monthly dashboards", "cross-functional alignment", "OKR tracking", "impact assessment", "growth advisory"
        ],
        "tools": [
            "ppt", "excel", "powerbi", "google sheets", "notion", "miro", "word", "asana", "dashboards", "confluence",
            "airtable", "jupyter", "analytics tool", "slides", "strategy tracker", "microsoft teams",
            "founder updates portal", "smartsheet", "google slides", "kpi dashboards"
        ],
        "domain": [
            "corporate strategy", "cx office", "high impact roles", "investment support", "founder engagement",
            "biz transformation", "planning", "team synergy", "adhoc projects", "competitive intelligence",
            "business enablement", "org growth", "ceo support", "startup advisory", "planning cycles",
            "key meetings support", "kpi mgmt", "leadership decks", "corporate reviews", "biz research"
        ],
        "education": [
            "mba", "btech", "ba eco", "bba", "pgdm", "mba strat", "mba finance", "msc", "mba ib", "mba innovation",
            "mba entrepreneurship", "mba leadership", "mba ops", "mba marketing", "mba analytics", "mba consulting",
            "mba transformation", "mba strategy & ops", "bcom", "msc econ"
        ]
    },
    ("customer excellence", "manager"): {
        "skills": [
            "feedback mgmt", "nps tracking", "root cause analysis", "customer journey", "service delivery",
            "crm escalation", "customer satisfaction", "email reply mgmt", "ticket resolution", "quality audits",
            "escalation matrix", "process improvement", "complaint tracking", "cx analysis", "call center mgmt",
            "net promoter score", "csat", "voice of customer", "response time reduction", "resolution effectiveness"
        ],
        "tools": [
            "zendesk", "crm", "freshdesk", "google forms", "call center tech", "email tools", "dashboard",
            "excel", "ppt", "confluence", "survey monkey", "hubspot", "ticketing software", "nps dashboard",
            "google sheets", "feedback tool", "intercom", "jira", "csat reports", "analytics dashboards"
        ],
        "domain": [
            "cx", "service quality", "issue resolution", "escalation handling", "retention", "customer support",
            "process improvement", "cx strategy", "client mgmt", "csat", "nps improvement", "service metrics",
            "customer loyalty", "customer onboarding", "voice of customer", "root cause resolution",
            "feedback strategy", "customer experience design", "customer insights", "touchpoint analysis"
        ],
        "education": [
            "mba", "bba", "graduate", "pgdm", "msc quality", "mba ops", "msc analytics", "bcom", "bms", "mba marketing",
            "certification cx", "mba service", "ba", "msc", "mba analytics", "mba digital", "mba crm", "pg cx program",
            "mba customer insight", "diploma in service mgmt"
        ]
    },
    ("learning & development", "am"): {
        "skills": [
            "training delivery", "learning need analysis", "e-learning", "program facilitation",
            "capability building", "content creation", "training calendar", "feedback analysis", "coaching",
            "talent development", "workshop facilitation", "instructional design", "blended learning",
            "learning analytics", "leadership development", "learning ROI", "behavioral training",
            "microlearning", "skills assessment", "training impact evaluation"
        ],
        "tools": [
            "lms", "ppt", "excel", "google classroom", "zoom", "teams", "slido", "google forms", "moodle", "email",
            "canva", "storyline", "articulate", "kirkpatrick model", "google sheets", "keka lms", "workday learning",
            "ms word", "quizizz", "assessment tool"
        ],
        "domain": [
            "capability building", "training ops", "organizational development", "employee engagement", "hrd",
            "skill enhancement", "leadership training", "upskilling", "learning design", "behavioral training",
            "performance improvement", "learning experience", "learning intervention", "competency development",
            "functional training", "training lifecycle", "talent capability", "training need identification",
            "skills gap analysis", "digital learning"
        ],
        "education": [
            "pgdm", "mba hr", "ma psychology", "bba", "msc hr", "mba learning", "bcom", "ba education", "b.ed", "mba",
            "certificate in l&d", "learning diploma", "hr cert", "mba talent dev", "msc learning design",
            "diploma org dev", "certification hr analytics", "mba capability dev", "msc behavioral science", "msc t&d"
        ]
    },
    ("reinsurance", "manager"): {
        "skills": [
            "underwriting", "reinsurance treaties", "loss ratio analysis", "risk assessment", "quota share",
            "facultative treaty", "pricing models", "risk aggregation", "retention management", "claims payout",
            "retrocession", "exposure analysis", "reinsurance broking", "policy wording", "treaty drafting",
            "risk modeling", "portfolio analysis", "claims accounting", "reinsurance billing", "recovery tracking"
        ],
        "tools": [
            "excel", "underwriting software", "reinsurance platform", "crm", "analytics suite", "sql", "risk tool",
            "ppt", "sas", "email", "inhouse re tools", "data warehouse", "r", "vba", "ms access", "powerbi",
            "risk dashboards", "actuarial tools", "re reporting", "policy software"
        ],
        "domain": [
            "risk underwriting", "insurance", "reinsurance", "actuarial", "policy structuring", "insurance finance",
            "retrocession", "treaty mgmt", "claims mgmt", "global risk", "ceding", "policy portfolio", "loss triangles",
            "re analytics", "co-insurance", "risk retention", "treaty operations", "technical accounting", "excess of loss", "stop-loss treaty"
        ],
        "education": [
            "actuarial science", "mba insurance", "mba", "ca", "pg diploma insurance", "bcom", "llb", "msc statistics",
            "mba finance", "ba eco", "cert reinsurance", "pg risk mgmt", "mba risk", "bba", "msc insurance",
            "bsc actuarial", "insurance certification", "fiii", "aca", "pg risk & finance"
        ]
    },
    ("oem & dealership", "dm"): {
        "skills": [
            "dealer onboarding", "inventory tracking", "sales mgmt", "pricing", "billing coordination",
            "stock transfer", "partner mgmt", "dispatch", "lead mgmt", "territory planning",
            "distribution mgmt", "invoicing", "stock allocation", "credit management", "vehicle allocation",
            "dealer relationship", "channel support", "logistics coordination", "route planning", "demand forecasting"
        ],
        "tools": [
            "dealer mgmt system", "erp", "excel", "crm", "sap", "email", "ppt", "salesforce", "inventory tool",
            "dashboards", "google sheets", "oracle", "zoho", "dispatch system", "route optimizer", "sales tracker",
            "stock dashboard", "pricing tool", "delivery tracking system", "dealer portal"
        ],
        "domain": [
            "automotive", "distribution", "retail operations", "channel partner", "stock allocation", "dealer mgmt",
            "b2b sales", "supply chain", "vehicle ops", "trade finance", "automobile logistics", "retail networks",
            "dealer development", "inventory control", "credit operations", "automobile sales", "distribution channel",
            "retail distribution", "commercial vehicle mgmt", "spare parts supply"
        ],
        "education": [
            "mba ops", "btech", "mba", "pgdm", "bba", "bcom", "mba supply", "bms", "mba marketing", "msc",
            "pg diploma logistics", "automobile engineering", "mba scm", "mba auto mgmt", "bsc", "mba distribution",
            "mba transport", "mba strategy", "mba channel mgmt", "mba delivery ops"
        ]
    },
    ("renewal", "manager"): {
        "skills": [
            "retention", "policy renewal", "customer follow-up", "payment collection", "lapsed conversion",
            "win-back", "reminder calls", "nps", "crm updates", "premium calculation",
            "policy reactivation", "follow-up scripts", "customer engagement", "renewal closure", "renewal escalation",
            "collection coordination", "policy lapse tracking", "renewal funnel mgmt", "cross-sell during renewal", "auto-debit setup"
        ],
        "tools": [
            "crm", "excel", "dialer", "email", "policy admin system", "google sheets", "sms tool", "powerbi",
            "ppt", "telephony", "payment gateway", "renewal tracker", "ivr", "call recording tool", "reminder bot",
            "whatsapp communication", "lead mgmt system", "auto-dialer", "renewal dashboard", "sms blast system"
        ],
        "domain": [
            "renewals", "customer lifecycle", "policy mgmt", "health insurance", "term insurance", "insurance sales",
            "customer retention", "follow-up ops", "conversion funnel", "cx", "life insurance", "policy lapse mgmt",
            "renewal marketing", "service reactivation", "policy database mgmt", "auto-renewal", "premium tracking",
            "policy persistency", "premium recovery", "policy management system"
        ],
        "education": [
            "graduate", "bcom", "bba", "mba insurance", "pg diploma insurance", "mba", "msc", "bsc", "ba", "bms",
            "insurance certification", "cert irda", "mba crm", "mba sales", "mba cx", "insurance diploma", "mba marketing",
            "msc insurance mgmt", "mba strategy", "diploma renewal mgmt", "bba insurance"
        ]
    },
    ("partnership", "sm"): {
        "skills": [
            "channel mgmt", "partner acquisition", "bd", "contract negotiation", "account mgmt", "crm mgmt",
            "partner training", "forecasting", "pipeline mgmt", "relationship mgmt",
            "partner enablement", "stakeholder alignment", "partner satisfaction", "partner onboarding",
            "incentive structure mgmt", "distribution network mgmt", "quarterly business review", "joint marketing plans",
            "sales target alignment", "territory division"
        ],
        "tools": [
            "crm", "excel", "ppt", "hubspot", "email", "pipeline software", "microsoft teams", "notion", "zoho",
            "reporting dashboards", "partner portal", "salesforce", "kpi dashboard", "airtable", "slack", "contract management system",
            "powerbi", "google sheets", "qbr tracker"
        ],
        "domain": [
            "partnerships", "alliances", "bd", "sales strategy", "distribution", "saas channels", "account mgmt",
            "key accounts", "relationship mgmt", "vendor mgmt", "affiliate network", "reseller mgmt", "franchise partnerships",
            "market expansion", "channel development", "partner retention", "partner loyalty", "regional partnerships",
            "sales collaboration", "joint ventures"
        ],
        "education": [
            "mba", "bcom", "bba", "mba marketing", "mba sales", "pgdm", "mba bd", "mba strat", "btech", "msc",
            "mba partnerships", "mba alliance mgmt", "mba channel sales", "bms", "mba crm", "mba vendor mgmt",
            "mba distribution", "mba corporate relations", "mba growth", "pg partner mgmt"
        ]
    },
    ("procurement", "am"): {
        "skills": [
            "vendor mgmt", "po creation", "negotiation", "sourcing", "cost reduction", "rfq", "contract mgmt",
            "grn mgmt", "inventory mgmt", "order tracking", "supply evaluation", "vendor onboarding",
            "procurement strategy", "e-tendering", "spend analysis", "purchase planning", "rate contract mgmt",
            "compliance mgmt", "strategic sourcing", "price benchmarking"
        ],
        "tools": [
            "sap", "excel", "tally", "oracle procurement", "email", "rfq tool", "ppt", "erp", "google sheets",
            "vendor portal", "procurement tracker", "powerbi", "zoho books", "coupa", "ariba", "sharepoint",
            "purchase order software", "compliance tool", "supplier scorecard", "grn system"
        ],
        "domain": [
            "procurement", "supply chain", "vendor ops", "logistics", "material mgmt", "inventory", "purchasing",
            "warehousing", "finance", "admin ops", "contract management", "demand planning", "purchase strategy",
            "bulk buying", "e-auction", "vendor rating", "supplier relationship", "direct & indirect procurement",
            "international sourcing", "capex/opex purchases"
        ],
        "education": [
            "btech", "mba", "mba ops", "bcom", "pg diploma supply", "msc logistics", "mba procurement", "ba", "bms",
            "mba scm", "pg scm", "mba logistics", "bba ops", "diploma in procurement", "certified sourcing professional",
            "mba international trade", "mba vendor mgmt", "mba industrial mgmt", "mba purchasing", "mba materials"
        ]
    },
    ("product", "director"): {
        "skills": [
            "product vision", "go-to-market", "cross-functional leadership", "product roadmap", "market research",
            "kpi mgmt", "team mgmt", "growth metrics", "strategic planning", "portfolio mgmt", "product lifecycle mgmt",
            "value proposition", "customer discovery", "stakeholder alignment", "scaling product lines", "m&a strategy",
            "funding roadmap", "monetization strategy", "product benchmarking", "risk mitigation in product"
        ],
        "tools": [
            "figma", "jira", "miro", "confluence", "ppt", "excel", "powerbi", "notion", "trello", "productboard",
            "lucidchart", "airtable", "roadmunk", "tableau", "asana", "monday.com", "google analytics", "powerpoint",
            "dashboards", "product analytics tools"
        ],
        "domain": [
            "product strategy", "platform mgmt", "product lifecycle", "customer centric design", "saas product",
            "enterprise product", "mvp", "innovation mgmt", "agile", "market fit", "global product leadership",
            "growth product", "consumer internet", "b2b saas", "product discovery", "user retention",
            "product portfolio", "startup ecosystem", "scale-up stage", "cross-border product launch"
        ],
        "education": [
            "mba", "btech", "mba pm", "mba strategy", "msc product", "mba tech", "ba", "bdes", "mba marketing", "mba it",
            "mba innovation", "mba entrepreneurship", "mba systems", "pg product mgmt", "mba design", "mba uiux",
            "bca", "msc cs", "mba scm", "mba analytics"
        ]
    },
    ("insurer relation", "manager"): {
        "skills": [
            "insurer onboarding", "pricing negotiation", "sla management", "relationship handling", "claim coordination",
            "renewal support", "data exchange", "regulatory liaison", "underwriting support", "product filing",
            "network expansion", "contract drafting", "insurance reporting", "renewal renegotiation",
            "claims reporting", "policy documentation", "service quality tracking", "rate negotiation", "grievance handling", "regulatory audit support"
        ],
        "tools": [
            "crm", "excel", "policy admin system", "email", "ppt", "reporting tools", "ms office", "google sheets",
            "jira", "dashboard", "contract mgmt software", "compliance tracker", "airtable", "zoho crm",
            "sharepoint", "regulatory portal", "claim systems", "network directory", "sap"
        ],
        "domain": [
            "insurance operations", "insurer management", "underwriting", "network management", "insurance partners",
            "contract terms", "policy servicing", "alliance management", "health insurance", "motor insurance",
            "policy admin", "policy filing", "regulatory compliance", "third-party coordination", "payout settlements",
            "regulatory updates", "product coordination", "commission mgmt", "risk review", "policy onboarding"
        ],
        "education": [
            "mba", "bcom", "bba", "mba insurance", "pg diploma insurance", "bms", "graduate", "mba marketing", "llb",
            "msc", "insurance certification", "mba partnerships", "mba compliance", "pgdm insurance", "mba operations",
            "mba finance", "msc insurance mgmt", "mba risk mgmt", "ba economics", "mba regulation"
        ]
    },
    ("founder's office", "manager"): {
        "skills": [
            "business analysis", "special projects", "founder support", "investor deck", "competitor analysis",
            "data synthesis", "market scoping", "board presentation", "project tracking", "kpi ownership",
            "cross-functional coordination", "performance mgmt", "cx support", "org design", "dashboarding",
            "portfolio mgmt", "corporate governance", "restructuring support", "M&A prep", "business storytelling"
        ],
        "tools": [
            "ppt", "excel", "google sheets", "notion", "miro", "powerbi", "figma", "email", "word", "airtable",
            "asana", "tableau", "monday.com", "lucidchart", "ms project", "jira", "dashboards", "zoho projects",
            "strategy tools", "okrs tracker"
        ],
        "domain": [
            "strategy", "special initiatives", "new verticals", "growth ops", "business performance", "startup ops",
            "vc communication", "investor relations", "metrics mgmt", "research", "founder initiatives", "business model pivoting",
            "product market fit", "CXO support", "transformation office", "operating rhythms", "quarterly review",
            "cap table mgmt", "org level dashboarding", "resource optimization"
        ],
        "education": [
            "mba", "btech", "mba strategy", "mba marketing", "mba finance", "bba", "pgdm", "ba economics", "ca", "msc",
            "mba innovation", "mba entrepreneurship", "mba operations", "mba business design", "mba leadership",
            "mba transformation", "mba planning", "mba corporate", "msc strategy", "mba growth"
        ]
    },
    ("claims, inbound & onboarding", "am"): {
        "skills": [
            "claims coordination", "onboarding experience", "email handling", "tpa mgmt", "policy updates",
            "customer support", "document verification", "claim escalation", "payment follow-up", "mis tracking",
            "team handling", "process improvement", "customer follow-ups", "sla monitoring", "training new joinees",
            "query resolution", "policy rectification", "daily ops mgmt", "reporting dashboards", "quality monitoring"
        ],
        "tools": [
            "crm", "email client", "excel", "policy software", "ticketing tool", "ivr tool", "tally", "google forms",
            "shared drive", "sap", "powerbi", "call tracker", "dialer", "policy admin system", "dashboard tools",
            "service CRM", "ms office", "claim portal", "quality tracker", "zendesk"
        ],
        "domain": [
            "insurance process", "claims mgmt", "customer onboarding", "policy servicing", "support ops", "insurance support",
            "medical claims", "motor claims", "tpa coordination", "service delivery", "policy amendment", "ticket closure",
            "renewal calls", "customer interaction", "operations review", "turnaround time mgmt", "health insurance",
            "life insurance", "general insurance", "call center ops"
        ],
        "education": [
            "graduate", "bcom", "bba", "mba", "mba insurance", "pg diploma", "msc", "llb", "ba", "bsc",
            "insurance certification", "pgdm insurance", "mba ops", "mba crm", "mba service", "diploma insurance",
            "mba general mgmt", "mba healthcare", "msc insurance", "mba business", "pg insurance mgmt"
        ]
    },
    ("customer excellence", "avp"): {
        "skills": [
            "cx strategy", "escalation resolution", "service design", "voice of customer", "cx automation", "feedback loop",
            "nps strategy", "net promoter improvement", "ops efficiency", "team management", "root cause analysis",
            "cx transformation", "issue prioritization", "workflow optimization", "process audit", "quality frameworks",
            "customer insighting", "retention strategy", "csat mgmt", "coaching team"
        ],
        "tools": [
            "zendesk", "crm", "email", "powerbi", "excel", "dashboard tool", "slack", "jira", "ppt", "survey tools",
            "freshdesk", "google sheets", "cx platform", "call center software", "ticketing dashboard", "feedback platform",
            "csat tracker", "voC dashboard", "notion", "airtable"
        ],
        "domain": [
            "customer experience", "service quality", "cx governance", "support ops", "customer journey", "cx metrics",
            "call center", "nps", "retention", "customer loyalty", "customer centricity", "customer satisfaction",
            "support excellence", "experience mgmt", "digital cx", "employee-customer loop", "cx training", "feedback analysis",
            "quality audit", "service blueprinting"
        ],
        "education": [
            "mba", "btech", "mba operations", "mba marketing", "pgdm", "bba", "msc", "ca", "bcom", "ba",
            "mba cx", "mba crm", "msc quality", "mba customer strategy", "mba service design", "mba transformation",
            "mba digital", "mba leadership", "msc ops", "mba innovation", "mba strategy"
        ]
    },
    ("strategy & analytics", "avp"): {
        "skills": [
            "financial modeling", "growth strategy", "competitive benchmarking", "forecasting", "dashboard creation",
            "business case development", "kpi alignment", "revenue modeling", "cohort analysis", "board level insights",
            "hypothesis testing", "scenario planning", "cross-functional collaboration", "roi tracking", "data storytelling",
            "market entry analysis", "strategic initiatives", "business research", "advanced analytics", "valuation modeling"
        ],
        "tools": [
            "powerbi", "tableau", "excel", "sql", "ppt", "notion", "airtable", "python", "r", "google sheets",
            "looker", "qlikview", "sas", "ms access", "ms project", "jira", "business dashboard", "crm analytics",
            "google data studio", "matplotlib"
        ],
        "domain": [
            "corporate strategy", "analytics", "business intelligence", "revenue strategy", "go-to-market",
            "market scoping", "performance mgmt", "financial planning", "okrs", "data storytelling",
            "strategic projects", "cost benchmarking", "pricing strategy", "commercial analytics", "product profitability",
            "customer segmentation", "sales analytics", "data-driven planning", "roi optimization", "competitor intelligence"
        ],
        "education": [
            "mba", "mba finance", "mba analytics", "btech", "ca", "msc statistics", "mba strategy", "bba", "ba economics", "pgdm",
            "mba decision science", "mba business analytics", "msc data science", "mba operations", "mba consulting",
            "pg diploma analytics", "mba transformation", "mba insights", "mba global business", "msc quantitative finance"
        ]
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

def extract_keywords_from_text(text):
    words = re.split(r"[,\n;/\-–\| ]+", text)
    filtered = [w.strip().lower() for w in words if len(w.strip()) > 2]
    
    STOP_WORDS = set([
    "the", "and", "for", "with", "from", "that", "this", "your", "have",
    "will", "are", "was", "were", "you", "has", "had", "but", "not", "any",
    "per", "our", "their", "his", "her", "each", "all", "other", "such", "etc"
])

    filtered = [w for w in filtered if w not in STOP_WORDS]

    # Phrase-aware matching
    all_phrases = set()
    for role in ROLE_KEYWORDS.values():
        for field in ["skills", "tools", "domain", "education"]:
            all_phrases.update(role.get(field, []))

    for k, syns in SYNONYMS.items():
        all_phrases.add(k)
        all_phrases.update(syns)

    matched_phrases = match_phrases_from_text(text, all_phrases)

    # ⚠️ Add synonyms of matched terms too
    expanded = set(matched_phrases)
    for term in matched_phrases:
        expanded.update(SYNONYMS.get(term, []))

    combined = list(set(filtered + list(expanded)))

    return {
        "skills": combined,
        "tools": combined,
        "domain": combined,
        "education": combined
    }

# --- Helper: Match full phrases from text ---
def match_phrases_from_text(text, phrases):
    text_lower = text.lower()
    matched = set()
    for phrase in phrases:
        # Match full phrase using word boundaries
        pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        if re.search(pattern, text_lower):
            matched.add(phrase)
    return list(matched)
