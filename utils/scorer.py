# utils/scorer.py
# Improved scoring — Skill Match + Semantic + Section Weighted

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Load semantic model once
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# =============================================
# PART 1 — SKILLS DICTIONARY
# =============================================

TECH_SKILLS = [
    # Programming Languages
    "Python", "Java", "C programming", "C++", "JavaScript",
    "TypeScript", "HTML", "CSS", "SQL", "R programming",
    "Kotlin", "Swift", "PHP",

    # AI / ML
    "Machine Learning", "Deep Learning", "NLP",
    "Computer Vision", "TensorFlow", "Keras",
    "PyTorch", "Scikit-learn", "Transformers",
    "BERT", "spaCy", "NLTK", "OpenCV",
    "XGBoost", "Random Forest",

    # Data
    "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Plotly", "Power BI", "Tableau",
    "Data Analysis", "Data Visualization",
    "Statistics", "EDA",

    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite",
    "Firebase", "Oracle", "Redis",

    # Frameworks
    "Flask", "Django", "FastAPI", "Streamlit",
    "React", "Angular", "Node.js", "Spring Boot",

    # Cloud and Tools
    "AWS", "Azure", "Docker", "Git", "GitHub",
    "Linux", "Unix", "Jupyter",

    # Mobile
    "Android Studio", "Kotlin", "Firebase",
]

# =============================================
# SKILL ALIASES — alternate names for skills
# =============================================

SKILL_ALIASES = {
    # Python variations
    "Python"          : ["python", "python3", "py"],

    # ML variations
    "Machine Learning": ["machine learning", "ml",
                         "machinelearning"],
    "Deep Learning"   : ["deep learning", "dl",
                         "deeplearning"],
    "NLP": ["nlp","natural language processing",
                         "text mining"],

    "C programming" : ["c programming", " c ", "c language"],
    "R programming" : ["r programming", " r ", "r language"],

    # Library variations
    "Scikit-learn"    : ["scikit-learn", "sklearn",
                         "scikit learn", "sk-learn"],
    "TensorFlow"      : ["tensorflow", "tensor flow",
                         "tf"],
    "PyTorch"         : ["pytorch", "py torch",
                         "torch"],
    "OpenCV"          : ["opencv", "open cv",
                         "cv2"],

    # Data tools
    "Pandas"          : ["pandas", "pd"],
    "NumPy"           : ["numpy", "np"],
    "Matplotlib"      : ["matplotlib", "plt"],
    "Power BI"        : ["power bi", "powerbi",
                         "power-bi", "pbi"],
    "Tableau"         : ["tableau"],
    "Microsoft Excel" : ["excel", "ms excel",
                         "microsoft excel"],

    # Databases
    "MySQL"           : ["mysql", "my sql",
                         "my-sql"],
    "MongoDB"         : ["mongodb", "mongo",
                         "mongo db"],
    "PostgreSQL"      : ["postgresql", "postgres",
                         "postgre sql"],

    # Frameworks
    "Node.js"         : ["node.js", "node", "nodejs",
                         "node js"],
    "React"           : ["react", "reactjs",
                         "react.js"],
    "Angular"         : ["angular", "angularjs"],
    "Spring Boot"     : ["spring boot", "springboot",
                         "spring"],
    "FastAPI"         : ["fastapi", "fast api"],

    # Cloud
    "AWS"             : ["aws", "amazon web services",
                         "amazon aws"],
    "Azure"           : ["azure",
                         "microsoft azure"],
    "GCP"             : ["gcp",
                         "google cloud platform",
                         "google cloud"],

    # Tools
    "Git"             : ["git"],
    "GitHub"          : ["github", "git hub"],
    "Docker"          : ["docker",
                         "docker container"],
    "Kubernetes"      : ["kubernetes", "k8s"],
    "Jupyter"         : ["jupyter", "jupyter notebook",
                         "ipython"],

    # Mobile
    "Android Studio"  : ["android studio",
                         "android", "androidstudio"],
    "Kotlin"          : ["kotlin"],
    "Firebase"        : ["firebase",
                         "google firebase"],
}


# =============================================
# PART 2 — SKILL EXTRACTOR
# =============================================

def extract_skills(text):
    """
    Finds all known skills mentioned in text
    Handles alternate names and common variations
    """
    text_lower = text.lower()
    found_skills = []

    # Method 1 — Check main TECH_SKILLS list
    for skill in TECH_SKILLS:
        if skill.lower() in text_lower:
            if skill not in found_skills:
                found_skills.append(skill)

    # Method 2 — Check aliases
    for skill, aliases in SKILL_ALIASES.items():
        if skill not in found_skills:  # not already found
            for alias in aliases:
                if alias.lower() in text_lower:
                    found_skills.append(skill)
                    break  # found one alias, no need
                           # to check rest

    return found_skills

# =============================================
# PART 3 — SKILL MATCH SCORE
# =============================================

def match_skills(resume_skills, jd_skills):
    resume_lower = [s.lower() for s in resume_skills]

    matched = [s for s in jd_skills
               if s.lower() in resume_lower]

    missing = [s for s in jd_skills
               if s.lower() not in resume_lower]

    if len(jd_skills) == 0:
        match_percent = 0
    else:
        match_percent = round(
            len(matched) / len(jd_skills) * 100, 2
        )

    return {
        "matched"       : matched,
        "missing"       : missing,
        "match_percent" : match_percent
    }


# =============================================
# PART 4 — TF-IDF SCORE
# =============================================

def tfidf_score(resume_text, jd_text):
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(
            [resume_text, jd_text]
        )
        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )
        return round(float(similarity[0][0]) * 100, 2)
    except Exception as e:
        print(f"TF-IDF error: {e}")
        return 0


# =============================================
# PART 5 — SEMANTIC SCORE
# =============================================

def semantic_score(resume_text, jd_text):
    try:
        embeddings = semantic_model.encode([
            resume_text[:512],
            jd_text[:512]
        ])
        similarity = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )
        return round(float(similarity[0][0]) * 100, 2)
    except Exception as e:
        print(f"Semantic error: {e}")
        return 0


# =============================================
# PART 6 — SECTION WEIGHTED SCORE
# =============================================


def section_weighted_score(parsed_resume, jd_text):
    sections = parsed_resume.get('sections', {})

    skills_text   = sections.get('SKILLS', '')
    projects_text = sections.get('ACADEMIC PROJECTS',
                    sections.get('PROJECTS', ''))
    full_text     = ' '.join(sections.values())

    jd_skills = extract_skills(jd_text)
    if not jd_skills:
        return 0

    skills_match = match_skills(
        extract_skills(skills_text), jd_skills
    )['match_percent']

    projects_match = match_skills(
        extract_skills(projects_text), jd_skills
    )['match_percent']

    full_match = match_skills(
        extract_skills(full_text), jd_skills
    )['match_percent']

    # If skills section is small
    # give more weight to projects + full resume
    if skills_match < 30:
        return round(
            (skills_match   * 0.20) +
            (projects_match * 0.40) +
            (full_match     * 0.40), 2
        )
    else:
        return round(
            (skills_match   * 0.40) +
            (projects_match * 0.30) +
            (full_match     * 0.30), 2
        )

# =============================================
# PART 7 — FINAL COMBINED SCORE
# =============================================

def calculate_score(resume_text, jd_text,
                    parsed_resume=None):
    """
    Combined score using 3 methods:

    Skill match score     → 40%
    Semantic similarity   → 35%
    Section weighted      → 25%

    Future improvements:
    → Add experience year extraction
    → Add education level matching
    """
    # Score 1 — Skill matching
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(jd_text)
    skill_result  = match_skills(resume_skills, jd_skills)
    skill_score   = skill_result["match_percent"]

    # Score 2 — Semantic similarity
    sem_score = semantic_score(resume_text, jd_text)

    # Score 3 — Section weighted
    if parsed_resume:
        section_score = section_weighted_score(
            parsed_resume, jd_text
        )
    else:
        section_score = skill_score

    # Final weighted combination
    final_score = round(
        (skill_score   * 0.60) +
        (sem_score     * 0.10) +
        (section_score * 0.30), 2
    )

    return {
        "resume_skills"  : resume_skills,
        "jd_skills"      : jd_skills,
        "matched"        : skill_result["matched"],
        "missing"        : skill_result["missing"],
        "skill_score"    : skill_score,
        "semantic_score" : sem_score,
        "section_score"  : section_score,
        "final_score"    : final_score
    }