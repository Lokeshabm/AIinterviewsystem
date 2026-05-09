# AI Interview Preparation System - Offline Setup Guide

## Overview

This is a **fully offline** Django-based AI Interview Preparation System that works completely on **localhost without any internet dependency**. No API keys, no external services, no AI APIs required.

### ✅ What's Included

- ✓ 200+ interview questions across 10 categories (Python, Django, React, JavaScript, MongoDB, SQL, Java, HTML/CSS, HR, Project-based)
- ✓ Resume parser (PDF & DOCX support)
- ✓ Skill detection using keyword matching
- ✓ Dynamic question generation (5 questions based on resume skills)
- ✓ Local answer evaluation (keyword-based scoring 1-10)
- ✓ Browser features (Camera, Microphone, Web Speech API)
- ✓ Certificate generation (reportlab PDF)
- ✓ User authentication (Django auth)
- ✓ Interview history & dashboard
- ✓ All offline, no internet required

---

## System Requirements

- Python 3.8+
- Django 4.2
- SQLite (included with Python)
- No external AI API services needed

---

## Installation & Setup

### 1. Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Current dependencies (no AI APIs):**
- Django>=4.2,<5.0
- python-dotenv>=1.0.0
- reportlab>=4.0.0
- python-docx>=0.8.11
- PyPDF2>=3.0.0

### 3. Configure Environment

Edit `.env` file:

```env
DJANGO_SECRET_KEY=your-django-secret-key-change-this
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
MEDIA_ROOT=media
MEDIA_URL=/media/
```

**Note:** No API keys required. No internet dependency.

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

**Access the system:** `http://localhost:8000`

---

## How It Works

### 1. User Registration & Login

- Create account: `http://localhost:8000/register`
- Login: `http://localhost:8000/login`
- Dashboard: `http://localhost:8000/dashboard`

### 2. Upload Resume

- Supported formats: PDF, DOCX
- Extract skills automatically
- Display detected skills on dashboard

### 3. Interview Question Generation

**Process:**
1. Parse resume text locally
2. Detect skills using regex keyword matching against 10 categories
3. Sort skills by frequency
4. Generate 5 questions:
   - 4 technical questions from detected skill categories
   - 1 project-based or HR question

**Example:**
- Resume with "Python, Django, MongoDB" → Questions from Python, Django, MongoDB, + 1 HR question

### 4. Interview Page

**Features:**
- One question per screen
- Progress bar (Question 1/5, 2/5, etc.)
- 60-second timer per question
- Camera preview (getUserMedia)
- Microphone & speech recognition (Web Speech API)
- Type or speak your answer
- Next/Previous navigation
- Submit answer for evaluation

### 5. Answer Evaluation (Local)

**Scoring Algorithm (1-10 scale):**
- Base score: 5.0
- Word count: -2 if <10 words, +1 if >200, +0.5 if >50
- Technical keywords: +2 if ≥3 found, +0.5 if 1 found
- Examples: +1 if mentions "example/for instance/such as"
- Structure: +0.5 if organized ("first/second/finally")
- Nuance: +0.5 if shows understanding ("although/however/despite")
- Red flags: -1 if "I don't know" or "not sure"

**Keywords checked:**
```
because, example, implement, function, class, method, algorithm, structure, 
design, pattern, principle, concept, process, workflow, best practice, error, 
exception, handle, performance, optimize, scale, architecture, system
```

### 6. Results & Certificate

- View scores after interview
- Download PDF certificate for passed interviews (score ≥ 6.0)
- Certificate generated locally using reportlab
- No external services

---

## File Structure

```
interveiw/
├── .env                          # Environment config (no API keys)
├── requirements.txt              # Dependencies (offline only)
├── manage.py                     # Django CLI
├── db.sqlite3                    # Database
├── interview/
│   ├── models.py                 # Interview, Question, Response models
│   ├── views.py                  # All view logic
│   ├── utils.py                  # Core functions:
│   │                             #   - parse_resume()
│   │                             #   - extract_resume_skills()
│   │                             #   - generate_questions_from_resume()
│   │                             #   - evaluate_answer_with_ai()
│   │                             #   - build_certificate()
│   ├── questions_bank.py         # 200+ questions database
│   ├── forms.py                  # Django forms
│   ├── urls.py                   # URL routing
│   ├── templates/interview/
│   │   ├── base.html            # Base template
│   │   ├── login.html           # Login page
│   │   ├── register.html        # Registration page
│   │   ├── dashboard.html       # Resume upload
│   │   ├── interview.html       # Interview questions
│   │   ├── scores.html          # Results & certificates
│   └── static/interview/
│       ├── css/style.css        # Styling
│       └── js/interview.js      # Browser APIs & navigation
├── ai_interview_system/
│   ├── settings.py              # Django config (offline only)
│   ├── urls.py                  # Main URL router
│   ├── asgi.py
│   └── wsgi.py
└── media/                        # User uploads (resumes, certificates)
```

---

## Key Offline Components

### 1. Question Bank (`interview/questions_bank.py`)

```python
QUESTIONS_BANK = {
    'python': [20+ questions],
    'django': [20+ questions],
    'react': [20+ questions],
    'javascript': [20+ questions],
    'mongodb': [20+ questions],
    'sql': [20+ questions],
    'java': [20+ questions],
    'html_css': [20+ questions],
    'hr': [20+ questions],
    'project_based': [20+ questions],
}

SKILL_KEYWORDS = {
    'python': ['python', 'py', 'django', 'flask', ...],
    'javascript': ['javascript', 'js', 'node', 'nodejs', ...],
    ...
}
```

**Total: 200+ questions, all stored locally**

### 2. Resume Parser (`utils.py`)

```python
def parse_resume(file_obj, file_name):
    """Extract text from PDF or DOCX locally"""
    # PDF: PyPDF2
    # DOCX: python-docx
    # Returns: text string

def extract_resume_skills(resume_text):
    """Detect skills using regex keyword matching"""
    # Searches SKILL_KEYWORDS in resume text
    # Returns: {skill_category: frequency_count}
```

### 3. Question Generation (`utils.py`)

```python
def generate_questions_from_resume(resume_text, role):
    """Generate 5 questions based on skills"""
    # 1. Extract skills via regex
    # 2. Select top 4 skills
    # 3. Pick random question from each category
    # 4. Add 1 HR/project question
    # 5. Return JSON: {technical: [q1-q4], project: [q5], hr: []}
```

### 4. Answer Evaluation (`utils.py`)

```python
def evaluate_answer_with_ai(question, answer):
    """Score answer 1-10 using keyword matching & analysis"""
    # Algorithm:
    # - Word count analysis
    # - Technical keyword detection
    # - Example usage check
    # - Structure analysis
    # - Red flag detection
    # Returns: formatted evaluation string with Score/Strength/Weakness/Improvement
```

### 5. Certificate Generation (`utils.py`)

```python
def build_certificate(user, interview):
    """Generate PDF certificate locally with reportlab"""
    # Name, score, date
    # No external service calls
    # Returns: PDF BytesIO buffer
```

---

## Browser Features

### getUserMedia (Camera)

```javascript
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  .then(stream => { /* display video */ })
```

### Web Speech API (Microphone & Speech-to-Text)

```javascript
const recognition = new webkitSpeechRecognition();
recognition.lang = 'en-US';
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  // Update textarea with spoken text
}
```

**Note:** Web Speech API requires HTTPS in production (works on localhost)

---

## Testing the System

### 1. Test Resume Upload

```bash
# Create sample resume with keywords
# Example: "I have 5 years of Python and Django experience"
# Upload PDF/DOCX file
```

### 2. Test Question Generation

```bash
# After upload, verify questions are generated
# Should see 4 technical + 1 HR/project question
# Check that they match resume skills
```

### 3. Test Answer Evaluation

```bash
# Answer a question with:
# - Short answer (<10 words) → Low score (1-3)
# - Medium answer (50 words) + examples → Medium-High (6-8)
# - Long detailed answer + technical terms → High (8-10)
```

### 4. Test Certificate

```bash
# Score ≥ 6.0 → "Passed"
# Download PDF certificate
# Verify local generation (no internet call)
```

---

## Troubleshooting

### Issue: "Unable to generate questions"

**Cause:** Resume parsing error or no keywords detected

**Fix:**
1. Verify PDF/DOCX file is valid
2. Check resume contains tech keywords
3. Review error message in Django logs

### Issue: Web Speech API not working

**Cause:** Browser limitation or HTTPS required

**Fix:**
1. Use Chrome/Firefox/Edge
2. On localhost, speech should work
3. In production, HTTPS required
4. Fallback: Type answer instead

### Issue: Certificate download fails

**Cause:** Score < 6.0 (not passed)

**Fix:**
1. Improve answers to score ≥ 6.0
2. Check interview shows "Passed: True"

### Issue: Database errors

**Fix:**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

---

## Production Deployment

### Important Notes for Localhost Only

- Current setup is for **localhost development**
- For production:
  1. Set `DEBUG = False`
  2. Update `DJANGO_ALLOWED_HOSTS`
  3. Use HTTPS for Web Speech API
  4. Use production database (PostgreSQL recommended)
  5. Serve static files properly
  6. Set secure cookie flags

**Current config is optimized for localhost testing with DEBUG=True**

---

## Feature Checklist

- [x] No OpenAI integration
- [x] No Gemini integration
- [x] No OpenRouter integration
- [x] No external AI APIs
- [x] 200+ interview questions (local)
- [x] Resume parsing (PDF/DOCX)
- [x] Skill detection (keyword matching)
- [x] Dynamic question generation (5 questions)
- [x] Local answer evaluation (1-10 scoring)
- [x] Camera preview (getUserMedia)
- [x] Microphone access (Web Speech API)
- [x] Certificate generation (reportlab)
- [x] User authentication (Django)
- [x] Interview dashboard
- [x] Results history
- [x] Completely offline
- [x] No internet required
- [x] No API quota errors
- [x] Fully localhost compatible

---

## Next Steps

1. ✅ **Installation:** Follow setup steps above
2. ✅ **Testing:** Upload sample resume, take interview
3. ✅ **Customization:** Edit `questions_bank.py` to add more questions
4. ✅ **Deployment:** Modify for production if needed

---

## Support & Debugging

### Check Django Logs

```bash
python manage.py runserver --verbosity 2
```

### Test Database

```bash
python manage.py shell
>>> from interview.models import Interview
>>> Interview.objects.all()
```

### Verify Questions Bank

```bash
python manage.py shell
>>> from interview.questions_bank import QUESTIONS_BANK
>>> len(QUESTIONS_BANK['python'])  # Should be 20+
>>> QUESTIONS_BANK.keys()  # All 10 categories
```

---

## Summary

This is a **completely offline** interview preparation system:

- ✓ All 200+ questions stored locally
- ✓ Resume parsing on your computer
- ✓ Skill detection using Python regex
- ✓ Question generation using local logic
- ✓ Answer evaluation without any AI API
- ✓ Certificate generation with reportlab
- ✓ Works perfectly on localhost
- ✓ No internet connection needed
- ✓ No external services or APIs
- ✓ Ready to use immediately

**Run it now:**
```bash
python manage.py runserver
# Open http://localhost:8000
```

---

## License

This project is provided as-is for educational purposes.
