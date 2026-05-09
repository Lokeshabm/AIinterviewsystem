import os
import re
from django.conf import settings
from docx import Document
from PyPDF2 import PdfReader
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
from .questions_bank import QUESTIONS_BANK, SKILL_KEYWORDS

def parse_resume(file_obj, file_name):
    """Parse resume from PDF or DOCX file."""
    text = ''
    lowered = file_name.lower()
    if lowered.endswith('.pdf'):
        reader = PdfReader(file_obj)
        for page in reader.pages:
            text += page.extract_text() or ''
    elif lowered.endswith('.docx'):
        document = Document(file_obj)
        for paragraph in document.paragraphs:
            text += paragraph.text + '\n'
    else:
        raise ValueError('Unsupported file format. Please upload PDF or DOCX.')
    return text.strip()

def extract_resume_skills(resume_text):
    """
    Extract skills from resume text by matching against known keywords.
    
    Returns a dictionary with detected skills and their frequency.
    """
    resume_lower = resume_text.lower()
    detected_skills = {}
    
    for skill_category, keywords in SKILL_KEYWORDS.items():
        skill_count = 0
        for keyword in keywords:
            # Count occurrences of keyword in resume
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, resume_lower)
            skill_count += len(matches)
        
        if skill_count > 0:
            detected_skills[skill_category] = skill_count
    
    return detected_skills

def generate_questions_from_resume(resume_text, role):
    """
    Generate 5 interview questions based on detected resume skills.
    
    Returns a JSON-formatted string with technical, hr, and project questions.
    """
    # Extract skills from resume
    detected_skills = extract_resume_skills(resume_text)
    
    # If no skills detected, use general questions
    if not detected_skills:
        detected_skills = {
            'python': 1,
            'javascript': 1,
            'sql': 1,
            'html_css': 1,
            'hr': 1
        }
    
    # Sort skills by frequency (highest first)
    sorted_skills = sorted(detected_skills.items(), key=lambda x: x[1], reverse=True)
    
    # Select questions based on detected skills
    selected_questions = []
    
    # Prioritize technical questions
    skills_to_use = [skill[0] for skill in sorted_skills][:4]  # Use top 4 skills
    
    # Select 4 technical questions from detected skills
    for skill in skills_to_use:
        if skill in QUESTIONS_BANK:
            available_questions = QUESTIONS_BANK[skill]
            if available_questions:
                selected_question = random.choice(available_questions)
                selected_questions.append(selected_question)
    
    # Ensure we have exactly 5 questions
    while len(selected_questions) < 5:
        # Add HR or project-based questions
        if len(selected_questions) < 4:
            # Add project-based question
            if 'project_based' in QUESTIONS_BANK:
                project_questions = QUESTIONS_BANK['project_based']
                if project_questions:
                    selected_questions.append(random.choice(project_questions))
        else:
            # Add HR question
            if 'hr' in QUESTIONS_BANK:
                hr_questions = QUESTIONS_BANK['hr']
                if hr_questions:
                    selected_questions.append(random.choice(hr_questions))
    
    # Limit to exactly 5 questions
    selected_questions = selected_questions[:5]
    
    # Categorize questions for JSON output
    result = {
        'technical': [],
        'project': [],
        'hr': []
    }
    
    for q in selected_questions:
        if any(q in QUESTIONS_BANK.get(skill, []) for skill in skills_to_use):
            result['technical'].append(q)
        elif q in QUESTIONS_BANK.get('project_based', []):
            result['project'].append(q)
        elif q in QUESTIONS_BANK.get('hr', []):
            result['hr'].append(q)
        else:
            result['technical'].append(q)
    
    # Ensure we return exactly 5 questions
    result['technical'] = result['technical'][:4]
    result['project'] = result['project'][:1]
    result['hr'] = result['hr'][:0]
    
    # If we don't have enough, fill from the selected questions
    all_selected = selected_questions
    if not result['technical']:
        result['technical'] = all_selected[:4]
    if not result['project']:
        result['project'] = all_selected[4:5]
    
    import json
    return json.dumps(result)

def evaluate_answer_with_ai(question, answer):
    """
    Evaluate answer locally using keyword matching and length analysis.
    
    Returns a formatted evaluation string with score and feedback.
    """
    if not answer or len(answer.strip()) == 0:
        return "Score: 1/10\nStrength: N/A\nWeakness: No answer provided\nImprovement: Please provide a detailed answer."
    
    score = 5.0  # Base score
    strengths = []
    weaknesses = []
    improvements = []
    
    answer_lower = answer.lower()
    answer_words = len(answer.split())
    answer_chars = len(answer)
    
    # Check answer length
    if answer_words < 10:
        score -= 2
        weaknesses.append("Answer is too brief")
        improvements.append("Provide more detailed explanations and examples")
    elif answer_words > 200:
        score += 1
        strengths.append("Comprehensive response")
    elif answer_words > 50:
        score += 0.5
        strengths.append("Good level of detail")
    
    # Check for technical terms and keywords
    technical_keywords = [
        'because', 'example', 'implement', 'function', 'class', 'method',
        'algorithm', 'structure', 'design', 'pattern', 'principle', 'concept',
        'process', 'workflow', 'best practice', 'error', 'exception', 'handle',
        'performance', 'optimize', 'scale', 'architecture', 'system'
    ]
    
    keyword_count = 0
    for keyword in technical_keywords:
        if keyword in answer_lower:
            keyword_count += 1
    
    if keyword_count >= 3:
        score += 2
        strengths.append("Uses technical terminology")
    elif keyword_count >= 1:
        score += 0.5
    else:
        weaknesses.append("Lacks technical depth")
        improvements.append("Use more technical terminology and domain-specific concepts")
    
    # Check for specific answer qualities
    if any(word in answer_lower for word in ['although', 'however', 'despite', 'but']):
        score += 0.5
        strengths.append("Shows nuanced understanding")
    
    if any(word in answer_lower for word in ['example', 'for instance', 'such as']):
        score += 1
        strengths.append("Provides concrete examples")
    else:
        improvements.append("Include practical examples to illustrate your points")
    
    if any(word in answer_lower for word in ['first', 'second', 'third', 'finally', 'next']):
        score += 0.5
        strengths.append("Well-structured response")
    
    # Check for common mistakes or red flags
    if 'i don\'t know' in answer_lower or 'not sure' in answer_lower:
        score -= 1
        weaknesses.append("Shows uncertainty")
        improvements.append("Research and understand the topic better")
    
    # Ensure score is between 1 and 10
    score = max(1, min(10, score))
    
    # Default messages if empty
    if not strengths:
        strengths = ["Attempted to answer the question"]
    if not weaknesses:
        weaknesses = ["Could provide more technical depth"]
    if not improvements:
        improvements = ["Continue learning and practicing"]
    
    # Format evaluation output
    evaluation = f"""Score: {score:.1f}/10
Strength: {strengths[0]}
Weakness: {weaknesses[0]}
Improvement: {improvements[0]}"""
    
    return evaluation

def build_certificate(user, interview):
    """Generate a PDF certificate for passed interview."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(width / 2, height - 120, 'Certificate of Achievement')
    
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 170, f'Presented to {user.get_full_name() or user.username}')
    
    c.setFont('Helvetica', 12)
    c.drawCentredString(width / 2, height - 210, 'For successfully completing the AI Interview Preparation System interview.')
    c.drawCentredString(width / 2, height - 230, f'Final Score: {interview.total_score:.1f}/10')
    c.drawCentredString(width / 2, height - 250, f'Date: {interview.date.date()}')
    
    c.line(100, height - 320, width - 100, height - 320)
    
    c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(width / 2, height - 340, 'This certificate is generated locally by the AI Interview Preparation System.')
    
    c.save()
    buffer.seek(0)
    return buffer
