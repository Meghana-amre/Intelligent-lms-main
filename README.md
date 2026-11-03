# AI-Powered Intelligent Learning Management System (LMS)
**Final Year B.E. Computer Science & Engineering Capstone Project**

An intelligent self-learning and self-assessment web platform tailored for **High School Students** and **PUC & Degree (Engineering) Students**, built with Python (Flask 3.x), SQLite, Bootstrap 5, Chart.js, Mermaid.js, and genuine academic algorithms (TextRank & Decision Trees).

---

## 🚀 Quick Start Guide (Windows)

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11, 3.12, 3.13, or 3.14)

### 2. Setup Virtual Environment & Install Dependencies
Open PowerShell in the extracted folder:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
# (Or directly run using .\venv\Scripts\python.exe)

# Install required packages
.\venv\Scripts\pip install -r requirements.txt
```

### 3. Initialize & Seed Database (Optional - Pre-seeded database `lms.db` is already included)
```powershell
.\venv\Scripts\python.exe seed_questions.py
```

### 4. Verify System & Uniqueness Constraints
```powershell
# Run zero-duplicate assertion
.\venv\Scripts\python.exe verify_unique.py

# Run comprehensive unit test suite
.\venv\Scripts\python.exe test_app.py
```

### 5. Start the Web Server
```powershell
.\venv\Scripts\python.exe app.py
```
Open your browser and visit: **`http://127.0.0.1:5000`**

---

## 📁 Project Architecture & Structure

```
AI_Powered_LMS_Project/
│
├── app.py                      # Core Flask WSGI web server & REST API controllers
├── database.py                 # SQLite relational database schema & transactional queries
├── lms.db                      # Pre-seeded SQLite database with 216+ unique questions
├── seed_questions.py           # Question bank generator (91 High School + 125 PUC/Degree questions)
├── verify_unique.py            # Automated test asserting 0 duplicate questions in active tests
├── test_app.py                 # Automated unit tests covering all routes, APIs, and ML engines
├── summarizer.py               # TextRank NLP algorithm for extractive newspaper summarization
├── map_generator.py            # Linguistic pattern detector & adaptive Mermaid diagram generator
├── ml_engine.py                # Decision Tree classifier & K-Means for student performance profiling
├── requirements.txt            # Python dependencies (Flask, scikit-learn, numpy, networkx, nltk)
├── README.md                   # Complete project documentation & guide
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern styling, glassmorphism, responsive components, cards
│   └── js/
│       ├── test_runner.js      # Interactive test engine (instant 🟢/🔴 feedback, explanations, timer)
│       └── games.js            # 5 interactive educational IQ games with live database synchronization
│
└── templates/
    ├── base.html               # Global layout, glassmorphic navbar, footer, CDN imports
    ├── index.html              # Main Landing Dashboard & Student Category Selection
    ├── about.html              # Project documentation, architecture diagram, IEEE citations, Viva Q&A
    │
    ├── highschool/
    │   ├── dashboard.html      # High School Hub (4 core modules + performance card)
    │   ├── test.html           # 50-Question Subject MCQ Test (8 subjects, strict zero duplicates)
    │   ├── games.html          # Educational & IQ Games Arena (Biology, Math, History, Geography, GK)
    │   ├── map_method.html     # Map Method (Theory to dynamic Flowchart/Mind Map visualizer)
    │   ├── newspaper.html      # TextRank Newspaper Summarizer, Key Points & Concept Infographic
    │   └── performance.html    # High School Self-Assessment Dashboard & Recommendations
    │
    └── puc_degree/
        ├── dashboard.html      # PUC & Degree Technical Assessment Hub
        ├── test.html           # CET/JEE tests with 50 questions per subject; DSA has 5 questions per topic
        └── performance.html    # Overall and subject scores by assessment plus historical score charts
```

---

## 🎓 Key Academic & IEEE References for Viva Voce

1. **Newspaper Summarization (TextRank)**:
   - R. Mihalcea and P. Tarau, "TextRank: Bringing Order into Texts," in *Proceedings of the 2004 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 2004, pp. 404–411.
   - M. S. Joshi, K. S. Babu, and B. S. Rao, "An Enhanced TextRank Algorithm for Automated Text Summarization," in *2020 IEEE 5th International Conference on Computing Communication and Automation (ICCCA)*, 2020, pp. 782–786, doi: 10.1109/ICCCA49541.2020.9250810.

2. **Student Performance Analysis (Decision Trees & Educational Data Mining)**:
   - S. K. Mohamad and Z. Tasir, "Educational Data Mining: A Review," in *2013 9th International Conference on Information Technology in Asia (CITA)*, 2013, pp. 1–6.
   - P. Cortez and A. M. G. Silva, "Using Data Mining to Predict Secondary School Student Performance," in *Proceedings of 5th Annual Future Business Technology Conference (FUBUTEC)*, 2008.
