import random
import uuid

from sqlalchemy import select

from app.database import SessionLocal
from app.models.role import Role
from app.models.competency import Competency, RoleCompetency
from app.models.course import Course, CourseCompetency
from app.models.question import Question


# ============================================================
# MASTER DATA
# ============================================================

ROLES = [
    {
        "name": "Statistical Officer",
        "description": "Officer responsible for statistical production, survey operations, analysis, data quality and official statistics.",
    },
    {
        "name": "Data Analyst",
        "description": "Professional responsible for data analysis, visualization, reporting and data-driven decision support.",
    },
    {
        "name": "Data Scientist",
        "description": "Professional working with statistical modelling, machine learning, AI and advanced data science.",
    },
    {
        "name": "IT Officer",
        "description": "Officer responsible for IT systems, APIs, cloud infrastructure, cybersecurity and digital governance.",
    },
]

# Based on the SIH description: statistical, technical, digital-governance,
# behavioural and managerial competency areas.
COMPETENCIES = [
    # Statistical
    ("Survey Design", "Statistical", "Ability to design statistically sound surveys and questionnaires."),
    ("Sampling", "Statistical", "Knowledge of sampling methods used in statistical surveys."),
    ("National Accounts", "Statistical", "Understanding of concepts and methods used in national accounts."),
    ("Price Statistics", "Statistical", "Knowledge of methods used to produce and interpret price statistics."),
    ("Labour Statistics", "Statistical", "Knowledge of concepts, sources and methods for labour statistics."),
    ("Agricultural Statistics", "Statistical", "Knowledge of statistical methods and data sources for agriculture."),
    ("Industrial Statistics", "Statistical", "Knowledge of statistical methods and data sources for industry."),
    ("SDG Indicators", "Statistical", "Understanding of statistical indicators used to monitor Sustainable Development Goals."),
    ("Metadata Standards", "Statistical", "Ability to use and maintain metadata for statistical data."),
    ("Data Quality", "Statistical", "Ability to assess, monitor and improve statistical data quality."),
    ("Statistical Analysis", "Statistical", "Ability to apply statistical methods to analyse datasets."),

    # Technical
    ("Python", "Technical", "Programming and data analysis using Python."),
    ("R", "Technical", "Statistical computing and data analysis using R."),
    ("SQL", "Technical", "Ability to query, manipulate and analyse relational data."),
    ("Stata", "Technical", "Statistical analysis using Stata."),
    ("SPSS", "Technical", "Statistical analysis using SPSS."),
    ("SAS", "Technical", "Statistical analysis and data processing using SAS."),
    ("GIS", "Technical", "Use of geographic information systems for spatial analysis."),
    ("Data Visualization", "Technical", "Ability to communicate insights through charts and dashboards."),
    ("AI/ML", "Technical", "Knowledge of artificial intelligence and machine learning methods."),
    ("Cloud Computing", "Technical", "Understanding and use of cloud computing services."),
    ("APIs", "Technical", "Ability to consume and work with application programming interfaces."),
    ("Open Data", "Technical", "Understanding and use of open-data principles and platforms."),

    # Digital Governance
    ("Cybersecurity", "Digital Governance", "Understanding of cybersecurity principles and secure systems."),
    ("Data Privacy", "Digital Governance", "Understanding of data protection and privacy principles."),
    ("Digital Signatures", "Digital Governance", "Understanding and use of digital signature concepts."),
    ("Government Cloud", "Digital Governance", "Understanding of cloud infrastructure used in government environments."),
    ("Digital Public Infrastructure", "Digital Governance", "Understanding of digital public infrastructure and interoperable government services."),

    # Behavioural / Managerial
    ("Leadership", "Behavioural", "Ability to lead teams, initiatives and organisational change."),
    ("Communication", "Behavioural", "Ability to communicate analytical and technical findings clearly."),
    ("Project Management", "Managerial", "Ability to plan, execute and monitor projects."),
    ("Ethics", "Behavioural", "Understanding and application of ethical principles in public-sector work."),
    ("Decision Making", "Managerial", "Ability to make evidence-based and accountable decisions."),
    ("Change Management", "Managerial", "Ability to manage adoption of new processes and technologies."),
]

ROLE_COMPETENCIES = {
    "Statistical Officer": {
        "Survey Design": (4, True),
        "Sampling": (4, True),
        "National Accounts": (3, True),
        "Price Statistics": (3, False),
        "Labour Statistics": (3, False),
        "Agricultural Statistics": (3, False),
        "Industrial Statistics": (3, False),
        "SDG Indicators": (3, False),
        "Metadata Standards": (4, True),
        "Data Quality": (4, True),
        "Statistical Analysis": (4, True),
        "Python": (3, False),
        "R": (3, False),
        "SQL": (3, False),
        "GIS": (2, False),
        "Data Visualization": (3, False),
        "Communication": (4, True),
        "Ethics": (4, True),
    },
    "Data Analyst": {
        "Statistical Analysis": (4, True),
        "Python": (4, True),
        "R": (3, False),
        "SQL": (4, True),
        "Data Visualization": (4, True),
        "Data Quality": (3, False),
        "APIs": (3, False),
        "Open Data": (3, False),
        "Communication": (4, True),
        "Decision Making": (3, False),
    },
    "Data Scientist": {
        "Statistical Analysis": (4, True),
        "Python": (5, True),
        "R": (4, False),
        "SQL": (4, False),
        "AI/ML": (5, True),
        "Data Visualization": (3, False),
        "Data Quality": (4, True),
        "Cloud Computing": (3, False),
        "APIs": (3, False),
        "Communication": (4, False),
    },
    "IT Officer": {
        "SQL": (3, False),
        "Python": (3, False),
        "APIs": (4, True),
        "Cloud Computing": (4, True),
        "Government Cloud": (4, True),
        "Cybersecurity": (5, True),
        "Data Privacy": (4, True),
        "Digital Signatures": (3, False),
        "Digital Public Infrastructure": (4, True),
        "Open Data": (3, False),
        "Communication": (3, False),
        "Project Management": (3, False),
    },
}

COURSES = [
    {
        "title": "Python for Data Analysis",
        "description": "Python fundamentals, NumPy, Pandas and practical data analysis.",
        "provider": "Internal Training",
        "external_id": "PYTHON-001",
        "duration_minutes": 240,
        "level": "beginner",
        "competencies": {"Python": 3},
    },
    {
        "title": "Advanced Python for Data Science",
        "description": "Advanced Python programming and analytical workflows.",
        "provider": "Internal Training",
        "external_id": "PYTHON-002",
        "duration_minutes": 360,
        "level": "advanced",
        "competencies": {"Python": 5, "Data Visualization": 3},
    },
    {
        "title": "R for Statistical Analysis",
        "description": "Statistical computing, data manipulation and analysis using R.",
        "provider": "Internal Training",
        "external_id": "R-001",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"R": 4, "Statistical Analysis": 3},
    },
    {
        "title": "SQL Fundamentals",
        "description": "Relational databases, SQL queries and data manipulation.",
        "provider": "Internal Training",
        "external_id": "SQL-001",
        "duration_minutes": 180,
        "level": "beginner",
        "competencies": {"SQL": 3},
    },
    {
        "title": "Advanced SQL and Analytics",
        "description": "Advanced queries, joins, aggregation and analytical SQL.",
        "provider": "Internal Training",
        "external_id": "SQL-002",
        "duration_minutes": 300,
        "level": "advanced",
        "competencies": {"SQL": 5, "Data Quality": 4},
    },
    {
        "title": "Statistical Methods for Official Statistics",
        "description": "Core statistical methods used in official statistical systems.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-001",
        "duration_minutes": 360,
        "level": "intermediate",
        "competencies": {"Statistical Analysis": 4, "Data Quality": 4},
    },
    {
        "title": "Survey Sampling Techniques",
        "description": "Sampling methodologies for official statistical surveys.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-002",
        "duration_minutes": 300,
        "level": "advanced",
        "competencies": {"Sampling": 4, "Survey Design": 4},
    },
    {
        "title": "Survey Design Fundamentals",
        "description": "Questionnaire design, sampling frames and survey planning.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-003",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {"Survey Design": 4, "Sampling": 3},
    },
    {
        "title": "Data Quality and Metadata",
        "description": "Data quality dimensions, validation and statistical metadata.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-004",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Data Quality": 4, "Metadata Standards": 4},
    },
    {
        "title": "National Accounts Fundamentals",
        "description": "Core concepts and statistical methods used in national accounts.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-005",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"National Accounts": 4},
    },
    {
        "title": "Price and Labour Statistics",
        "description": "Methods and indicators used in price and labour statistics.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-006",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Price Statistics": 3, "Labour Statistics": 3},
    },
    {
        "title": "Agricultural and Industrial Statistics",
        "description": "Statistical sources, methods and indicators for agriculture and industry.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-007",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Agricultural Statistics": 3, "Industrial Statistics": 3},
    },
    {
        "title": "SDG Indicators and Open Data",
        "description": "SDG indicator concepts, dissemination and open-data practices.",
        "provider": "NSSTA Mock Catalogue",
        "external_id": "STAT-008",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {"SDG Indicators": 4, "Open Data": 3},
    },
    {
        "title": "Data Visualization and Storytelling",
        "description": "Effective visualizations, dashboards and communication of insights.",
        "provider": "Internal Training",
        "external_id": "VIZ-001",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {"Data Visualization": 4, "Communication": 4},
    },
    {
        "title": "Machine Learning Fundamentals",
        "description": "Supervised and unsupervised machine learning fundamentals.",
        "provider": "Internal Training",
        "external_id": "ML-001",
        "duration_minutes": 360,
        "level": "intermediate",
        "competencies": {"AI/ML": 3, "Python": 3},
    },
    {
        "title": "Applied AI and Machine Learning",
        "description": "Applied machine learning workflows, evaluation and deployment concepts.",
        "provider": "Internal Training",
        "external_id": "ML-002",
        "duration_minutes": 420,
        "level": "advanced",
        "competencies": {"AI/ML": 5, "Python": 5, "Data Visualization": 3},
    },
    {
        "title": "GIS for Statistical Applications",
        "description": "Spatial data, mapping and GIS-based statistical analysis.",
        "provider": "Internal Training",
        "external_id": "GIS-001",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"GIS": 4},
    },
    {
        "title": "Cloud Computing and Government Cloud",
        "description": "Cloud concepts, deployment models and government cloud environments.",
        "provider": "Internal Training",
        "external_id": "CLOUD-001",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Cloud Computing": 4, "Government Cloud": 4},
    },
    {
        "title": "APIs and Interoperable Government Services",
        "description": "REST APIs, integration patterns and interoperable digital services.",
        "provider": "Internal Training",
        "external_id": "API-001",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {"APIs": 4, "Digital Public Infrastructure": 3},
    },
    {
        "title": "Cybersecurity and Data Privacy",
        "description": "Security fundamentals, privacy principles and secure government systems.",
        "provider": "Government Training",
        "external_id": "SEC-001",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Cybersecurity": 4, "Data Privacy": 4},
    },
    {
        "title": "Digital Governance Essentials",
        "description": "Digital signatures, public digital infrastructure and government technology governance.",
        "provider": "Government Training",
        "external_id": "GOV-001",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {
            "Digital Signatures": 3,
            "Digital Public Infrastructure": 4,
            "Data Privacy": 3,
        },
    },
    {
        "title": "Leadership and Project Management",
        "description": "Leadership, planning, execution and stakeholder management.",
        "provider": "Internal Training",
        "external_id": "MGMT-001",
        "duration_minutes": 300,
        "level": "intermediate",
        "competencies": {"Leadership": 4, "Project Management": 4, "Communication": 3},
    },
    {
        "title": "Ethics and Evidence-Based Decision Making",
        "description": "Ethics, responsible use of data and evidence-based public-sector decisions.",
        "provider": "Government Training",
        "external_id": "MGMT-002",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {"Ethics": 4, "Decision Making": 4},
    },
]

# Three questions per competency gives the MVP assessment engine a usable
# question bank while keeping the seed manageable. Existing questions are
# updated by question text; no duplicates are created.
QUESTION_TEMPLATES = {
    "Survey Design": [
        ("Which feature is most important when designing a questionnaire?", "Clear and unbiased questions", "beginner"),
        ("What is a pilot survey primarily used for?", "Testing the questionnaire and survey procedures", "intermediate"),
        ("Leading questions are problematic because they can:", "Introduce response bias", "advanced"),
    ],
    "Sampling": [
        ("Which sampling method gives every population member an equal probability of selection?", "Simple random sampling", "beginner"),
        ("Stratified sampling divides a population into:", "Homogeneous subgroups before sampling", "intermediate"),
        ("A sampling frame is best described as:", "A list or representation from which the sample is selected", "advanced"),
    ],
    "National Accounts": [
        ("GDP is commonly used to measure:", "The value of final goods and services produced within an economy", "beginner"),
        ("National accounts provide a framework for:", "Measuring economic activity systematically", "intermediate"),
        ("In national accounts, production, income and expenditure approaches are used to:", "Measure the same economic activity from complementary perspectives", "advanced"),
    ],
    "Price Statistics": [
        ("A price index is generally used to measure:", "Changes in prices over time", "beginner"),
        ("The CPI is primarily associated with:", "Changes in the prices paid by households for a basket of goods and services", "intermediate"),
        ("Weighting in a price index reflects:", "The relative importance of items in the basket", "advanced"),
    ],
    "Labour Statistics": [
        ("Employment statistics generally measure:", "Participation in economic activity and work", "beginner"),
        ("The unemployment rate is calculated using:", "Unemployed people divided by the labour force", "intermediate"),
        ("Labour-force statistics are commonly used to analyse:", "Employment, unemployment and participation", "advanced"),
    ],
    "Agricultural Statistics": [
        ("Agricultural statistics commonly cover:", "Crops, livestock, land and agricultural production", "beginner"),
        ("Crop yield is generally expressed as:", "Production per unit of cultivated area", "intermediate"),
        ("Agricultural surveys may use area and production data to:", "Estimate agricultural output", "advanced"),
    ],
    "Industrial Statistics": [
        ("Industrial statistics commonly measure:", "Production and activity in industrial sectors", "beginner"),
        ("An industrial production index measures:", "Changes in industrial output over time", "intermediate"),
        ("Industrial classification systems help:", "Group economic activities consistently", "advanced"),
    ],
    "SDG Indicators": [
        ("SDG indicators are used to:", "Monitor progress toward Sustainable Development Goals", "beginner"),
        ("A good statistical indicator should be:", "Relevant, measurable and well-defined", "intermediate"),
        ("Disaggregation of SDG indicators helps identify:", "Differences across population groups or regions", "advanced"),
    ],
    "Metadata Standards": [
        ("Statistical metadata primarily describes:", "The concepts, methods and context behind data", "beginner"),
        ("Metadata improves data:", "Interpretability and reuse", "intermediate"),
        ("A standardised metadata structure helps:", "Improve consistency and interoperability", "advanced"),
    ],
    "Data Quality": [
        ("Which is a common dimension of data quality?", "Accuracy", "beginner"),
        ("Validation rules are used to:", "Detect invalid or inconsistent data", "intermediate"),
        ("A quality framework helps organisations:", "Systematically monitor and improve data quality", "advanced"),
    ],
    "Statistical Analysis": [
        ("Which measure represents the middle value of an ordered dataset?", "Median", "beginner"),
        ("Correlation measures:", "The strength and direction of association between variables", "intermediate"),
        ("A confidence interval provides:", "A range of plausible values for a population parameter", "advanced"),
    ],
    "Python": [
        ("Which Python library is commonly used for tabular data analysis?", "Pandas", "beginner"),
        ("Which Python structure is commonly used to store key-value pairs?", "Dictionary", "intermediate"),
        ("In Pandas, a DataFrame represents:", "A two-dimensional labelled data structure", "advanced"),
    ],
    "R": [
        ("R is widely used for:", "Statistical computing and data analysis", "beginner"),
        ("Which object is commonly used for tabular data in R?", "Data frame", "intermediate"),
        ("R packages are primarily used to:", "Extend R with reusable functionality", "advanced"),
    ],
    "SQL": [
        ("Which SQL statement retrieves data from a table?", "SELECT", "beginner"),
        ("Which SQL clause filters rows?", "WHERE", "intermediate"),
        ("Which SQL operation combines rows from related tables?", "JOIN", "advanced"),
    ],
    "Stata": [
        ("Stata is commonly used for:", "Statistical analysis", "beginner"),
        ("Stata commands are primarily used to:", "Manage and analyse datasets", "intermediate"),
        ("Stata do-files are useful for:", "Reproducible analysis workflows", "advanced"),
    ],
    "SPSS": [
        ("SPSS is commonly used for:", "Statistical analysis", "beginner"),
        ("SPSS supports:", "Data management and statistical procedures", "intermediate"),
        ("Using syntax in SPSS improves:", "Reproducibility of analysis", "advanced"),
    ],
    "SAS": [
        ("SAS is widely used for:", "Data processing and statistical analysis", "beginner"),
        ("SAS programs commonly contain:", "DATA and PROC steps", "intermediate"),
        ("SAS is particularly useful for:", "Large-scale structured data processing and analysis", "advanced"),
    ],
    "GIS": [
        ("GIS is primarily used to analyse:", "Geographically referenced data", "beginner"),
        ("A GIS layer represents:", "A collection of related geographic features or information", "intermediate"),
        ("Spatial analysis can be used to:", "Identify geographic patterns and relationships", "advanced"),
    ],
    "Data Visualization": [
        ("Which chart is appropriate for the distribution of a continuous variable?", "Histogram", "beginner"),
        ("A scatter plot is useful for showing:", "The relationship between two numerical variables", "intermediate"),
        ("Effective dashboards should primarily:", "Communicate relevant insights clearly", "advanced"),
    ],
    "AI/ML": [
        ("Which type of machine learning uses labelled training data?", "Supervised learning", "beginner"),
        ("Overfitting occurs when a model:", "Learns training data too closely and generalises poorly", "intermediate"),
        ("Cross-validation is commonly used to:", "Estimate model performance on unseen data", "advanced"),
    ],
    "Cloud Computing": [
        ("Cloud computing provides:", "On-demand computing resources over a network", "beginner"),
        ("IaaS primarily provides:", "Virtualised computing infrastructure", "intermediate"),
        ("Cloud elasticity means:", "Resources can scale with demand", "advanced"),
    ],
    "APIs": [
        ("An API allows:", "Software systems to communicate with each other", "beginner"),
        ("REST APIs commonly use:", "HTTP methods", "intermediate"),
        ("API authentication is used to:", "Verify the identity or permissions of a client", "advanced"),
    ],
    "Open Data": [
        ("Open data is data that is:", "Available for access and reuse subject to its licence", "beginner"),
        ("Open-data standards improve:", "Discoverability and interoperability", "intermediate"),
        ("Publishing metadata with open data helps users:", "Understand and correctly reuse the dataset", "advanced"),
    ],
    "Cybersecurity": [
        ("Which practice adds a security layer beyond a password?", "Multi-factor authentication", "beginner"),
        ("Encryption is primarily used to:", "Protect information from unauthorised access", "intermediate"),
        ("Least privilege means users should:", "Receive only the access required for their work", "advanced"),
    ],
    "Data Privacy": [
        ("Purpose limitation means personal data should be:", "Collected and processed for specified purposes", "beginner"),
        ("Data minimisation means:", "Collecting only data necessary for the purpose", "intermediate"),
        ("Access controls help protect personal data by:", "Restricting access to authorised users", "advanced"),
    ],
    "Digital Signatures": [
        ("A digital signature is used primarily to provide:", "Authenticity and integrity", "beginner"),
        ("Digital signatures commonly rely on:", "Public-key cryptography", "intermediate"),
        ("A valid digital signature helps demonstrate that:", "The signed data was associated with the signer and was not altered", "advanced"),
    ],
    "Government Cloud": [
        ("Government cloud environments are designed to support:", "Secure and controlled government workloads", "beginner"),
        ("Cloud governance includes:", "Policies for security, access and resource management", "intermediate"),
        ("Government cloud controls should address:", "Security, compliance and operational requirements", "advanced"),
    ],
    "Digital Public Infrastructure": [
        ("Digital public infrastructure aims to provide:", "Reusable digital systems and services for public benefit", "beginner"),
        ("Interoperability allows systems to:", "Exchange and use information across platforms", "intermediate"),
        ("Reusable digital public infrastructure can improve:", "Scale and consistency of public digital services", "advanced"),
    ],
    "Leadership": [
        ("Effective leadership involves:", "Guiding people toward shared objectives", "beginner"),
        ("Delegation means:", "Assigning responsibility and authority appropriately", "intermediate"),
        ("Good leaders should use feedback to:", "Improve team and individual performance", "advanced"),
    ],
    "Communication": [
        ("Effective communication should be:", "Clear and appropriate for the audience", "beginner"),
        ("Data storytelling helps:", "Explain analytical findings in an understandable way", "intermediate"),
        ("When presenting complex analysis, an effective approach is to:", "Focus on the key message and supporting evidence", "advanced"),
    ],
    "Project Management": [
        ("A project plan defines:", "Activities, resources, timelines and responsibilities", "beginner"),
        ("Risk management involves:", "Identifying, assessing and responding to risks", "intermediate"),
        ("A project milestone represents:", "A significant point or achievement in the project", "advanced"),
    ],
    "Ethics": [
        ("Ethical data use requires:", "Responsible and fair handling of information", "beginner"),
        ("Conflict of interest should be:", "Declared and managed appropriately", "intermediate"),
        ("Statistical ethics emphasise:", "Integrity, impartiality and responsible use of evidence", "advanced"),
    ],
    "Decision Making": [
        ("Evidence-based decision making relies on:", "Relevant and reliable evidence", "beginner"),
        ("A decision matrix can help:", "Compare alternatives against defined criteria", "intermediate"),
        ("Sensitivity analysis examines:", "How results change when assumptions or inputs change", "advanced"),
    ],
    "Change Management": [
        ("Change management focuses on:", "Helping people and organisations adopt change", "beginner"),
        ("Stakeholder engagement helps:", "Build understanding and support for change", "intermediate"),
        ("Successful technology adoption often requires:", "Communication, training and ongoing support", "advanced"),
    ],
}


def make_question_data(competency_name, index, question_text, answer, difficulty):
    # Build four MCQ options with plausible, domain-specific distractors.
    # The correct answer is shuffled into a random position so it is
    # not always option A.
    domain = next(
        (d for n, d, _ in COMPETENCIES if n == competency_name),
        "General",
    )

    distractor_pool = {
        "Statistical": [
            "An outdated method no longer recommended for official statistics",
            "A technique used mainly for qualitative research",
            "A measure that applies only to census data",
            "A concept from experimental rather than survey design",
            "A method requiring complete population enumeration",
        ],
        "Technical": [
            "A manual spreadsheet-based approach",
            "A function from a different library with unrelated behaviour",
            "A concept that applies only to unstructured text data",
            "A legacy approach replaced by modern frameworks",
            "A technique for static reporting rather than interactive analysis",
        ],
        "Digital Governance": [
            "A consumer-grade technology without government safeguards",
            "A manual process that does not require digital infrastructure",
            "A practice applicable only to private-sector organisations",
            "A protocol that replaces rather than complements existing standards",
            "A concept from physical rather than digital security",
        ],
        "Behavioural": [
            "An individual preference unrelated to organisational outcomes",
            "A short-term tactic rather than a sustained capability",
            "A skill that applies only to external stakeholder communication",
            "An innate trait that cannot be developed through training",
            "A theoretical concept with no practical application",
        ],
        "Managerial": [
            "An ad-hoc activity rather than a structured process",
            "A one-time event rather than a recurring governance mechanism",
            "A financial metric rather than a project oversight tool",
            "An individual task rather than a team coordination activity",
            "A static plan that does not adapt to changing requirements",
        ],
    }.get(domain, [
        "An outdated approach no longer considered best practice",
        "A narrow view that ignores broader context",
        "A method that applies only to idealised conditions",
        "A theoretical concept with limited practical use",
        "An alternative that contradicts standard frameworks",
    ])

    import random

    distractors = random.sample(distractor_pool, k=min(3, len(distractor_pool)))
    options = {
        "A": answer,
        "B": distractors[0],
        "C": distractors[1],
        "D": distractors[2],
    }

    keys = list(options.keys())
    random.shuffle(keys)
    shuffled_options = {key: options[key] for key in keys}
    correct_key = next(key for key, value in shuffled_options.items() if value == answer)

    return {
        "competency": competency_name,
        "question_text": question_text,
        "question_type": "mcq",
        "difficulty": difficulty,
        "options": shuffled_options,
        "correct_answer": correct_key,
        "explanation": answer,
    }


def seed_database():
    db = SessionLocal()

    try:
        print("Starting database seed...")
        print()

        # --------------------------------------------------------
        # 1. ROLES
        # --------------------------------------------------------
        role_map = {}

        for data in ROLES:
            role = db.scalar(select(Role).where(Role.name == data["name"]))

            if role is None:
                role = Role(
                    id=uuid.uuid4(),
                    name=data["name"],
                    description=data["description"],
                    is_active=True,
                )
                db.add(role)
                db.flush()
            else:
                role.description = data["description"]
                role.is_active = True

            role_map[role.name] = role

        print(f"Roles ready: {len(role_map)}")

        # --------------------------------------------------------
        # 2. COMPETENCIES
        # --------------------------------------------------------
        competency_map = {}

        for name, domain, description in COMPETENCIES:
            competency = db.scalar(
                select(Competency).where(Competency.name == name)
            )

            if competency is None:
                competency = Competency(
                    id=uuid.uuid4(),
                    name=name,
                    domain=domain,
                    description=description,
                    is_active=True,
                )
                db.add(competency)
                db.flush()
            else:
                competency.domain = domain
                competency.description = description
                competency.is_active = True

            competency_map[name] = competency

        print(f"Competencies ready: {len(competency_map)}")

        # --------------------------------------------------------
        # 3. ROLE -> COMPETENCY
        # --------------------------------------------------------
        role_mapping_count = 0

        for role_name, mappings in ROLE_COMPETENCIES.items():
            role = role_map[role_name]

            for competency_name, (required_level, is_critical) in mappings.items():
                competency = competency_map[competency_name]

                existing = db.scalar(
                    select(RoleCompetency).where(
                        RoleCompetency.role_id == role.id,
                        RoleCompetency.competency_id == competency.id,
                    )
                )

                if existing is None:
                    existing = RoleCompetency(
                        id=uuid.uuid4(),
                        role_id=role.id,
                        competency_id=competency.id,
                        required_level=required_level,
                        is_critical=is_critical,
                        organizational_priority=2 if is_critical else 1,
                    )
                    db.add(existing)
                else:
                    existing.required_level = required_level
                    existing.is_critical = is_critical

                role_mapping_count += 1

        print(f"Role-competency mappings ready: {role_mapping_count}")

        # --------------------------------------------------------
        # 4. COURSES
        # --------------------------------------------------------
        course_map = {}

        for data in COURSES:
            course = db.scalar(
                select(Course).where(Course.external_id == data["external_id"])
            )

            if course is None:
                course = Course(
                    id=uuid.uuid4(),
                    title=data["title"],
                    description=data["description"],
                    provider=data["provider"],
                    source="mock",
                    external_id=data["external_id"],
                    url=f"https://example.com/courses/{data['external_id'].lower()}",
                    duration_minutes=data["duration_minutes"],
                    level=data["level"],
                    is_active=True,
                )
                db.add(course)
                db.flush()
            else:
                course.title = data["title"]
                course.description = data["description"]
                course.provider = data["provider"]
                course.source = "mock"
                course.duration_minutes = data["duration_minutes"]
                course.level = data["level"]
                course.url = f"https://example.com/courses/{data['external_id'].lower()}"
                course.is_active = True

            course_map[data["external_id"]] = course

        print(f"Courses ready: {len(course_map)}")

        # --------------------------------------------------------
        # 5. COURSE -> COMPETENCY
        # --------------------------------------------------------
        course_mapping_count = 0

        for data in COURSES:
            course = course_map[data["external_id"]]

            for competency_name, target_level in data["competencies"].items():
                competency = competency_map[competency_name]

                existing = db.scalar(
                    select(CourseCompetency).where(
                        CourseCompetency.course_id == course.id,
                        CourseCompetency.competency_id == competency.id,
                    )
                )

                if existing is None:
                    existing = CourseCompetency(
                        id=uuid.uuid4(),
                        course_id=course.id,
                        competency_id=competency.id,
                        target_level=target_level,
                    )
                    db.add(existing)
                else:
                    existing.target_level = target_level

                course_mapping_count += 1

        print(f"Course-competency mappings ready: {course_mapping_count}")

        # --------------------------------------------------------
        # 6. QUESTION BANK
        # --------------------------------------------------------
        question_count = 0

        for competency_name, questions in QUESTION_TEMPLATES.items():
            for index, (question_text, answer, difficulty) in enumerate(questions, start=1):
                data = make_question_data(
                    competency_name,
                    index,
                    question_text,
                    answer,
                    difficulty,
                )

                competency = competency_map[competency_name]

                existing = db.scalar(
                    select(Question).where(
                        Question.question_text == data["question_text"]
                    )
                )

                if existing is None:
                    existing = Question(
                        id=uuid.uuid4(),
                        competency_id=competency.id,
                        question_text=data["question_text"],
                        question_type=data["question_type"],
                        difficulty=data["difficulty"],
                        options=data["options"],
                        correct_answer=data["correct_answer"],
                        explanation=data["explanation"],
                        is_active=True,
                    )
                    db.add(existing)
                else:
                    existing.competency_id = competency.id
                    existing.question_type = data["question_type"]
                    existing.difficulty = data["difficulty"]
                    existing.options = data["options"]
                    existing.correct_answer = data["correct_answer"]
                    existing.explanation = data["explanation"]
                    existing.is_active = True

                question_count += 1

        print(f"Question bank ready: {question_count}")

        db.commit()

        print()
        print("========================================")
        print("DATABASE SEED COMPLETED")
        print("========================================")
        print(f"Roles:                  {len(role_map)}")
        print(f"Competencies:           {len(competency_map)}")
        print(f"Role mappings:          {role_mapping_count}")
        print(f"Courses:                {len(course_map)}")
        print(f"Course mappings:        {course_mapping_count}")
        print(f"Questions processed:    {question_count}")
        print("Existing users untouched")
        print("Assessments untouched")
        print("Answers untouched")
        print("User competencies untouched")
        print("Progress untouched")
        print("Recommendations untouched")
        print("========================================")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
