# Quick Start Guide - Offline AI Interview System

## 🚀 Get Running in 3 Minutes

### Step 1: Activate Virtual Environment
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start Server
```bash
python manage.py runserver
```

### Step 4: Open Browser
```
http://localhost:8000
```

---

## 🎯 Test the System (5 Minutes)

### 1. Create Account
- Click "Register"
- Username: `testuser`
- Email: `test@example.com`
- Password: `testpass123`

### 2. Upload Resume
- Dashboard → Upload Resume
- **Create a test resume with:**
  ```
  Skills: Python, Django, MongoDB, React
  Experience: 5 years in full-stack development
  ```
- Save as PDF or DOCX
- Upload file

### 3. Take Interview
- Click "Start Interview"
- You'll see **5 questions** based on resume skills:
  - 4 technical questions (Python, Django, MongoDB, React)
  - 1 HR/project question
- Answer each question (or use microphone 🎤)
- Timer: 60 seconds per question
- Camera preview working ✅

### 4. Get Results
- Answer all questions
- Click "Submit Answer" after each
- View evaluation:
  - **Score:** 1-10
  - **Strength:** What you did well
  - **Weakness:** What to improve
  - **Suggestion:** How to improve
- See if you **Passed** (score ≥ 6.0)

### 5. Download Certificate
- If passed: Download PDF certificate
- Certificate shows name, score, date
- Generated locally (no cloud upload)

---

## 🎮 Features You'll Experience

✅ **Camera** - Live video preview (getUserMedia)
✅ **Microphone** - Speak your answers (Web Speech API)
✅ **Timer** - 60 seconds per question
✅ **Progress** - See question 1/5, 2/5, etc.
✅ **Navigation** - Previous/Next buttons
✅ **Evaluation** - Instant feedback (offline scoring)
✅ **Certificate** - PDF download (reportlab)
✅ **History** - View all past interviews

---

## 🔍 Key Files

| File | Purpose |
|------|---------|
| `interview/questions_bank.py` | 200+ questions in 10 categories |
| `interview/utils.py` | Core logic: parse resume, generate questions, evaluate answers |
| `interview/views.py` | Django request handlers |
| `interview/models.py` | Database: Interview, Question, Response |
| `interview/static/js/interview.js` | Browser APIs: camera, microphone, timer |
| `.env` | Config (no API keys needed) |
| `requirements.txt` | Dependencies (all offline) |

---

## ⚙️ Customize

### Add More Questions
Edit `interview/questions_bank.py`:
```python
QUESTIONS_BANK = {
    'python': [
        'What is a lambda function?',
        'Your new question here',  # ← Add here
        ...
    ]
}
```

### Change Scoring Algorithm
Edit `evaluate_answer_with_ai()` in `interview/utils.py`:
```python
score = 5.0  # Base score
# Add/remove scoring logic
score += bonus_for_length
score += bonus_for_keywords
```

### Add Skill Keywords
Edit `SKILL_KEYWORDS` in `interview/questions_bank.py`:
```python
SKILL_KEYWORDS = {
    'python': ['python', 'py', 'django', 'flask', 'your-keyword-here'],
}
```

---

## 🐛 Troubleshooting

### Q: "Unable to generate questions"
**A:** Resume might not have tech keywords. Try:
```
Skills: Python, Django, MongoDB, React, JavaScript, SQL
```

### Q: "Web Speech API not working"
**A:** Browser issue (use Chrome/Firefox/Edge). Fallback: Type instead.

### Q: "Can't upload resume"
**A:** Make sure file is PDF or DOCX, not corrupted.

### Q: "Certificate not available"
**A:** Score must be ≥ 6.0 to pass. Improve your answers!

### Q: "Database error"
**A:** Reset database:
```bash
rm db.sqlite3
python manage.py migrate
```

---

## 📊 What Happens Behind the Scenes

1. **Upload Resume**
   ```
   Your PDF/DOCX → parse_resume() → Extract text locally
   ```

2. **Detect Skills**
   ```
   Resume text → extract_resume_skills() → Regex keyword matching
   Result: {python: 5, django: 3, mongodb: 2, react: 1}
   ```

3. **Generate Questions**
   ```
   Skills → generate_questions_from_resume() → Random selection
   Result: 5 questions matching your skills (no duplicates)
   ```

4. **Evaluate Answer**
   ```
   Your answer → evaluate_answer_with_ai() → Keyword analysis
   Result: Score 1-10 + Feedback
   ```

5. **Certificate**
   ```
   Score + Name + Date → build_certificate() → PDF file
   ```

**Everything happens locally - no internet calls!**

---

## 🔐 Privacy & Security

✅ Resume stored locally (media folder)
✅ Answers stored in local SQLite database
✅ No cloud sync or upload
✅ No AI company access
✅ No tracking or telemetry
✅ No API keys to leak

---

## 💡 Pro Tips

1. **Speech Recognition:** Speak clearly, microphone close to mouth
2. **Better Scoring:** Answer with examples and technical terms
3. **Multiple Interviews:** Upload different resumes to test various skills
4. **Offline Guaranteed:** Unplug internet after starting server - still works!
5. **Production Mode:** Change `DJANGO_DEBUG=False` in .env when deploying

---

## 📚 Learn More

- **Full Setup:** See `OFFLINE_SETUP.md`
- **Technical Details:** See `CONVERSION_COMPLETE.md`
- **Code Structure:** See comments in `interview/utils.py`

---

## 🎉 You're Ready!

```bash
python manage.py runserver
# Open http://localhost:8000
# Take your first interview right now!
```

**No API keys. No internet. No limits.** 

Just you, your resume, and the interview system! 🚀

---
