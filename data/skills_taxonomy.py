"""Skill vocabulary (canonical name -> aliases) and role blueprints.

Used by (a) the resume parser to detect skills and (b) the job generator to
simulate a labour market. Swap for ESCO / O*NET / Lightcast in production.
"""

SKILLS: dict[str, list[str]] = {
    # --- Engineering / cloud
    "Python": ["python3"], "SQL": ["mysql", "postgresql", "postgres", "t-sql"],
    "Java": [], "JavaScript": ["js", "ecmascript"], "TypeScript": [],
    "React": ["react.js", "reactjs"], "Node.js": ["nodejs", "node js"],
    "HTML/CSS": ["html", "css", "html5", "css3"], "Git": ["github", "gitlab"],
    "Docker": ["containerization"], "Kubernetes": ["k8s"], "AWS": ["amazon web services"],
    "Azure": ["microsoft azure"], "GCP": ["google cloud", "google cloud platform"],
    "Linux": ["unix", "bash"], "CI/CD": ["ci cd", "continuous integration", "jenkins", "github actions"],
    "REST APIs": ["rest api", "restful", "rest", "api development"],
    "FastAPI": [], "Django": [], "Flask": [],
    # --- Data / AI
    "Machine Learning": ["ml"], "Deep Learning": ["neural networks"],
    "NLP": ["natural language processing"], "PyTorch": [], "TensorFlow": ["keras"],
    "Scikit-learn": ["sklearn", "scikit learn"], "Pandas": [], "NumPy": [],
    "Data Visualization": ["data visualisation", "matplotlib", "seaborn", "dashboards"],
    "Tableau": [], "Power BI": ["powerbi"], "Excel": ["microsoft excel", "ms excel", "spreadsheets"],
    "Statistics": ["statistical analysis", "hypothesis testing"], "A/B Testing": ["ab testing", "a/b tests"],
    "ETL": ["data pipelines", "data pipeline"], "Apache Spark": ["spark", "pyspark"],
    "Airflow": ["apache airflow"], "Data Modeling": ["data modelling", "data warehousing"],
    "MLOps": ["mlflow", "model deployment"],
    # --- Security
    "Cybersecurity": ["information security", "infosec"], "Network Security": ["firewalls"],
    "Penetration Testing": ["pentesting", "ethical hacking"], "SIEM": ["splunk"],
    # --- Product / management / design
    "Project Management": ["pmp", "project planning"], "Agile/Scrum": ["agile", "scrum", "kanban"],
    "Product Management": ["product roadmap"], "Stakeholder Management": ["stakeholder engagement"],
    "Communication": ["communication skills", "presentation skills"], "Leadership": ["team leadership", "people management"],
    "UX Design": ["ux", "ui/ux", "user experience"], "Figma": [], "User Research": ["usability testing"],
    # --- Marketing / sales
    "SEO": ["search engine optimization"], "Content Marketing": ["copywriting", "content strategy"],
    "Google Analytics": ["ga4"], "Social Media Marketing": ["social media"], "Email Marketing": ["mailchimp"],
    "CRM": ["hubspot"], "Salesforce": [], "Sales Strategy": ["b2b sales", "lead generation"], "Negotiation": [],
    # --- Finance
    "Financial Modeling": ["financial modelling", "valuation"], "Accounting": ["bookkeeping", "gaap", "ifrs"],
    "Budgeting": ["forecasting", "budget management"], "Risk Management": ["risk assessment"],
    "Regulatory Compliance": ["compliance", "regulatory affairs"], "Auditing": ["internal audit", "audit"],
    # --- Health
    "Patient Care": ["clinical care", "nursing care"], "Electronic Health Records": ["ehr", "emr"],
    "Clinical Research": ["clinical trials"], "Public Health": ["epidemiology"], "Health Informatics": ["healthcare analytics"],
    # --- Education / HR / ops
    "Curriculum Design": ["lesson planning"], "Instructional Design": ["adult learning"],
    "Classroom Management": [], "E-learning": ["elearning", "lms"],
    "Supply Chain Management": ["logistics", "procurement", "supply chain"], "Lean Manufacturing": ["lean", "kaizen"],
    "Six Sigma": [], "CAD": ["autocad", "solidworks"], "PLC Programming": ["plc", "scada"],
    "Quality Assurance": ["qa", "test automation", "quality control"],
    "Solar PV Design": ["solar design", "pv systems"], "Energy Auditing": ["energy audit", "energy efficiency"],
    "Sustainability Reporting": ["esg reporting", "esg", "gri standards"], "Environmental Compliance": ["environmental regulations"],
    "Technical Writing": ["documentation"], "Customer Service": ["customer support", "customer success"],
    "Recruitment": ["talent acquisition", "recruiting"], "HR Analytics": ["people analytics", "hris"],
}

# role -> (industry, core skills, optional skills)
ROLES: dict[str, tuple[str, list[str], list[str]]] = {
    # Technology
    "Backend Developer": ("Technology", ["Python", "REST APIs", "SQL", "Git", "Docker"], ["FastAPI", "Django", "Flask", "AWS", "Linux", "CI/CD", "Node.js", "Java"]),
    "Frontend Developer": ("Technology", ["JavaScript", "TypeScript", "React", "HTML/CSS", "Git"], ["REST APIs", "Figma", "UX Design", "Node.js"]),
    "Full Stack Developer": ("Technology", ["JavaScript", "React", "Node.js", "SQL", "REST APIs", "Git"], ["TypeScript", "Docker", "AWS", "Python"]),
    "DevOps Engineer": ("Technology", ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Git"], ["Python", "Azure", "GCP"]),
    "Cloud Engineer": ("Technology", ["AWS", "Linux", "Docker", "Kubernetes"], ["Azure", "GCP", "Python", "CI/CD", "Git"]),
    "Cybersecurity Analyst": ("Technology", ["Cybersecurity", "Network Security", "SIEM", "Linux", "Risk Management"], ["Penetration Testing", "Python", "Regulatory Compliance"]),
    "QA Engineer": ("Technology", ["Quality Assurance", "Python", "Git", "Agile/Scrum"], ["REST APIs", "CI/CD", "SQL", "JavaScript"]),
    "UX Designer": ("Technology", ["UX Design", "Figma", "User Research", "Communication"], ["A/B Testing", "HTML/CSS"]),
    # Data & AI
    "Data Analyst": ("Data & AI", ["SQL", "Excel", "Data Visualization", "Statistics", "Tableau"], ["Power BI", "Python", "Google Analytics", "Pandas"]),
    "Data Scientist": ("Data & AI", ["Python", "Machine Learning", "Statistics", "Pandas", "SQL", "Scikit-learn"], ["Deep Learning", "NumPy", "Data Visualization", "A/B Testing"]),
    "Machine Learning Engineer": ("Data & AI", ["Python", "Machine Learning", "PyTorch", "Docker", "MLOps", "Git"], ["TensorFlow", "AWS", "Kubernetes", "Deep Learning"]),
    "NLP Engineer": ("Data & AI", ["Python", "NLP", "PyTorch", "Deep Learning", "Machine Learning"], ["TensorFlow", "Docker", "FastAPI"]),
    "Data Engineer": ("Data & AI", ["Python", "SQL", "ETL", "Apache Spark", "Airflow", "Data Modeling"], ["AWS", "Docker", "Kubernetes", "Git"]),
    "BI Developer": ("Data & AI", ["SQL", "Power BI", "Data Modeling", "ETL", "Excel"], ["Tableau", "Python", "Data Visualization"]),
    # Healthcare
    "Registered Nurse": ("Healthcare", ["Patient Care", "Electronic Health Records", "Communication"], ["Public Health", "Customer Service", "Regulatory Compliance"]),
    "Clinical Research Coordinator": ("Healthcare", ["Clinical Research", "Regulatory Compliance", "Electronic Health Records", "Communication"], ["Statistics", "Excel", "Technical Writing"]),
    "Health Informatics Specialist": ("Healthcare", ["Health Informatics", "Electronic Health Records", "SQL", "Data Visualization", "Regulatory Compliance"], ["Python", "Statistics"]),
    "Public Health Analyst": ("Healthcare", ["Public Health", "Statistics", "Data Visualization", "Excel", "Technical Writing"], ["SQL", "Python"]),
    # Finance
    "Financial Analyst": ("Finance", ["Financial Modeling", "Excel", "Accounting", "Budgeting"], ["SQL", "Power BI", "Risk Management", "Data Visualization"]),
    "Accountant": ("Finance", ["Accounting", "Excel", "Auditing", "Budgeting", "Regulatory Compliance"], ["Communication", "SQL"]),
    "Risk Analyst": ("Finance", ["Risk Management", "Statistics", "Excel", "Regulatory Compliance", "Financial Modeling"], ["Python", "SQL"]),
    "Internal Auditor": ("Finance", ["Auditing", "Accounting", "Regulatory Compliance", "Risk Management", "Excel"], ["Communication", "Technical Writing"]),
    # Marketing & Sales
    "Digital Marketing Specialist": ("Marketing & Sales", ["SEO", "Content Marketing", "Google Analytics", "Social Media Marketing", "Email Marketing"], ["A/B Testing", "CRM"]),
    "Sales Executive": ("Marketing & Sales", ["Sales Strategy", "CRM", "Negotiation", "Communication", "Salesforce"], ["Customer Service"]),
    "Marketing Analyst": ("Marketing & Sales", ["Google Analytics", "SQL", "Data Visualization", "A/B Testing", "Excel"], ["Python", "Tableau"]),
    "Content Strategist": ("Marketing & Sales", ["Content Marketing", "SEO", "Communication", "Technical Writing"], ["Social Media Marketing", "Google Analytics"]),
    # Manufacturing & Green Energy
    "Supply Chain Analyst": ("Manufacturing & Green Energy", ["Supply Chain Management", "Excel", "SQL", "Data Visualization"], ["Power BI", "Lean Manufacturing", "Risk Management"]),
    "Manufacturing Engineer": ("Manufacturing & Green Energy", ["Lean Manufacturing", "Six Sigma", "CAD", "Quality Assurance", "PLC Programming"], ["Project Management", "Excel"]),
    "Solar Energy Engineer": ("Manufacturing & Green Energy", ["Solar PV Design", "CAD", "Energy Auditing", "Project Management", "Environmental Compliance"], ["Excel", "Technical Writing"]),
    "Sustainability Analyst": ("Manufacturing & Green Energy", ["Sustainability Reporting", "Environmental Compliance", "Excel", "Data Visualization", "Energy Auditing"], ["Statistics", "Python", "Technical Writing"]),
    # Education & HR
    "Instructional Designer": ("Education & HR", ["Instructional Design", "Curriculum Design", "E-learning", "Communication", "Technical Writing"], ["Figma", "Project Management"]),
    "Teacher": ("Education & HR", ["Curriculum Design", "Classroom Management", "Communication", "Instructional Design"], ["E-learning", "Leadership"]),
    "HR Specialist": ("Education & HR", ["Recruitment", "HR Analytics", "Communication", "Regulatory Compliance", "Excel"], ["CRM", "Leadership"]),
    # Business & Operations
    "Project Manager": ("Business & Operations", ["Project Management", "Agile/Scrum", "Stakeholder Management", "Communication", "Budgeting", "Risk Management"], ["Leadership", "Excel"]),
    "Product Manager": ("Business & Operations", ["Product Management", "Agile/Scrum", "Stakeholder Management", "Communication", "A/B Testing"], ["SQL", "User Research", "Data Visualization", "Google Analytics"]),
    "Customer Success Manager": ("Business & Operations", ["Customer Service", "CRM", "Communication", "Stakeholder Management"], ["Salesforce", "Leadership", "Excel"]),
    "Operations Manager": ("Business & Operations", ["Leadership", "Project Management", "Budgeting", "Lean Manufacturing", "Communication"], ["Supply Chain Management", "Six Sigma", "Excel"]),
}
INDUSTRIES = sorted({v[0] for v in ROLES.values()})
