# 📄 Resume Ranker — AI Powered Recruitment Tool

An AI-powered web application that helps recruiters
screen and rank multiple resumes against a job description
using NLP and Machine Learning.

## 🌐 Live Demo
[Click here to try the app](https://your-app-link.streamlit.app)

## 🎯 Features
- Upload multiple resumes (PDF or DOCX)
- Paste any job description
- AI-powered scoring using 3 methods
- Interactive ranking table with medals
- Skill gap analysis per candidate
- Downloadable PDF report
- Interactive Plotly charts

## 🧠 How Scoring Works
| Method | Weight | Description |
|---|---|---|
| Skill Matching | 40% | Keyword + alias matching |
| Semantic Score | 25% | SentenceTransformers embeddings |
| Section Score | 35% | Section weighted skill matching |

## 🛠️ Tech Stack
| Category | Tools |
|---|---|
| Language | Python 3.12 |
| NLP | spaCy, SentenceTransformers |
| ML | Scikit-learn (TF-IDF) |
| PDF | PyMuPDF, ReportLab |
| Web | Streamlit |
| Charts | Plotly |
| Data | Pandas, NumPy |

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/SwathiHT/resume-ranker.git
cd resume-ranker
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install libraries
```bash
pip install -r requirements.txt
```

### 4. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 5. Run the app
```bash
streamlit run app/dashboard.py
```

## 📊 Screenshots
*(Add screenshots here after deployment)*

## 🔮 Future Improvements
- Experience year extraction
- Education level matching
- Fuzzy matching for typos
- Database for past sessions