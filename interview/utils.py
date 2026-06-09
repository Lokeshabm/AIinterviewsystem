import hashlib
import json
import os
import random
import re
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image
from django.conf import settings
from docx import Document
from PyPDF2 import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
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


def _select_bank_questions_for_resume(detected_skills, count, exclude=None):
    exclude = set(exclude or [])
    selected = []
    seen = set(exclude)

    # Use the most relevant skills first.
    skills_to_use = [skill for skill, _ in sorted(detected_skills.items(), key=lambda x: x[1], reverse=True)]
    random.shuffle(skills_to_use)

    for skill in skills_to_use:
        if len(selected) >= count:
            break
        available = [q for q in QUESTIONS_BANK.get(skill, []) if q not in seen]
        if not available:
            continue
        question = random.choice(available)
        selected.append({'text': question, 'category': 'technical'})
        seen.add(question)

    # Add one project-based and one HR question if needed.
    if len(selected) < count and 'project_based' in QUESTIONS_BANK:
        available = [q for q in QUESTIONS_BANK['project_based'] if q not in seen]
        if available:
            question = random.choice(available)
            selected.append({'text': question, 'category': 'project'})
            seen.add(question)

    if len(selected) < count and 'hr' in QUESTIONS_BANK:
        available = [q for q in QUESTIONS_BANK['hr'] if q not in seen]
        if available:
            question = random.choice(available)
            selected.append({'text': question, 'category': 'hr'})
            seen.add(question)

    # Fill the remainder with any unseen technical questions.
    if len(selected) < count:
        all_technical = [q for cat, questions in QUESTIONS_BANK.items() if cat not in ('project_based', 'hr') for q in questions if q not in seen]
        random.shuffle(all_technical)
        for question in all_technical:
            if len(selected) >= count:
                break
            selected.append({'text': question, 'category': 'technical'})
            seen.add(question)

    return selected[:count]


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
    Generate 5 interview questions based on resume content and the candidate role.

    Uses the internal QUESTIONS_BANK only.
    Returns a JSON-formatted string with technical, project, and hr question lists.
    """
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

    questions = _select_bank_questions_for_resume(detected_skills, 5)

    result = {
        'technical': [],
        'project': [],
        'hr': []
    }

    for q in questions[:5]:
        category = q.get('category', 'technical') if isinstance(q, dict) else 'technical'
        text = q['text'] if isinstance(q, dict) else q
        if category not in result:
            category = 'technical'
        result[category].append(text)

    # Fill shorter categories with technical questions if necessary
    total_questions = sum(len(vals) for vals in result.values())
    if total_questions < 5:
        extra = _select_bank_questions_for_resume(detected_skills, 5 - total_questions, exclude=[q for vals in result.values() for q in vals])
        for q in extra:
            category = q.get('category', 'technical')
            if category not in result:
                category = 'technical'
            result[category].append(q['text'])

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

def _generate_verification_code(candidate_id):
    digest = hashlib.sha256(candidate_id.encode('utf-8')).hexdigest().upper()
    return digest[:8]


def _generate_qr_image(data, size=160):
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    return img.resize((size, size), Image.NEAREST)


def build_certificate(user, interview, candidate_id=None, certificate_id=None):
    """Generate a styled PDF certificate matching the uploaded design."""
    if candidate_id is None or certificate_id is None:
        year = interview.date.year
        candidate_id = f'BML-{year}-{interview.id:06d}'
        certificate_id = f'CERT-{year}-{interview.id:06d}'

    verification_code = _generate_verification_code(candidate_id)
    verification_url = 'https://verify.bmlcertificate.com'
    recipient = user.get_full_name() or user.username
    program_name = interview.role or 'Advanced Achievement Program'

    buffer = BytesIO()
    page_size = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    # Background and border
    c.setFillColor(colors.HexColor('#f8f3e1'))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor('#b78c29'))
    c.setLineWidth(18)
    c.rect(25, 25, width - 50, height - 50, stroke=1, fill=0)
    c.setStrokeColor(colors.HexColor('#e6d4a8'))
    c.setLineWidth(8)
    c.rect(45, 45, width - 90, height - 90, stroke=1, fill=0)

    # Watermark
    c.saveState()
    c.setFillColor(colors.HexColor('#d4b36e'))
    c.setFont('Helvetica-Bold', 90)
    c.drawCentredString(width / 2, height / 2 + 10, 'Excellence')
    c.restoreState()

    # Header brand
    c.setFillColor(colors.HexColor('#1f2f5a'))
    c.setFont('Helvetica-Bold', 18)
    c.drawString(80, height - 90, 'BML')
    c.setFont('Helvetica', 9)
    c.drawString(80, height - 108, 'Presented by')
    c.setFont('Helvetica-Bold', 16)
    c.drawString(80, height - 132, 'Business & Management Leadership')

    # Title block
    c.setFont('Times-Bold', 34)
    c.drawCentredString(width / 2, height - 130, 'CERTIFICATE OF ACHIEVEMENT')
    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#4b5161'))
    c.drawCentredString(width / 2, height - 150, 'This is to certify that')

    # Recipient name and candidate ID
    c.setFillColor(colors.HexColor('#13274c'))
    c.setFont('Helvetica-Bold', 42)
    c.drawCentredString(width / 2, height - 210, recipient)
    c.setFont('Helvetica', 12)
    c.setFillColor(colors.HexColor('#1f365d'))
    c.drawCentredString(width / 2, height - 235, f'Candidate ID: {candidate_id}')

    # Achievement text
    c.setFillColor(colors.HexColor('#2c3555'))
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 280, 'Has demonstrated exceptional ability and successfully completed the')
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(width / 2, height - 305, program_name)
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 330, 'with outstanding professionalism, technical mastery, and leadership qualities.')

    # Detail cards
    card_width = (width - 240) / 3
    card_height = 85
    card_y = height - 430
    card_x = 80
    card_titles = ['Organization', 'Completion Date', 'Grade / Performance']
    card_values = [
        'Global Engineering Institute',
        interview.date.strftime('%B %d, %Y'),
        'Distinction',
    ]

    for index, title in enumerate(card_titles):
        x = card_x + index * (card_width + 15)
        c.setStrokeColor(colors.HexColor('#d8c78a'))
        c.setFillColor(colors.HexColor('#ffffff'))
        c.rect(x, card_y, card_width, card_height, stroke=1, fill=1)
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#5a5c7d'))
        c.drawString(x + 12, card_y + card_height - 18, title)
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#143056'))
        c.drawString(x + 12, card_y + card_height - 40, card_values[index])

    # Signatures and seal
    signature_y = height - 520
    c.setStrokeColor(colors.HexColor('#20335f'))
    c.setLineWidth(1.4)
    c.line(90, signature_y + 14, 290, signature_y + 14)
    c.line(width - 310, signature_y + 14, width - 110, signature_y + 14)

    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#20335f'))
    c.drawString(90, signature_y - 4, 'Program Coordinator')
    c.drawString(width - 310, signature_y - 4, 'Founder & Director')

    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(width / 2, signature_y + 4, 'Official Seal')
    c.setStrokeColor(colors.HexColor('#c8a55b'))
    c.setLineWidth(3)
    seal_radius = 50
    c.circle(width / 2, signature_y + 10, seal_radius, stroke=1, fill=0)
    c.setFont('Helvetica', 8)
    c.drawCentredString(width / 2, signature_y - 8, 'Verified Seal')

    c.setFont('Helvetica-Bold', 14)
    c.drawString(width - 290, signature_y + 16, 'B M Lokesha')
    c.setFont('Helvetica', 10)
    c.drawString(width - 290, signature_y - 4, 'Founder & Director')

    # Verification footer
    footer_x = 80
    footer_y = 70
    footer_width = width - 160
    footer_height = 120
    c.setStrokeColor(colors.HexColor('#c4b287'))
    c.setFillColor(colors.HexColor('#ffffff'))
    c.rect(footer_x, footer_y, footer_width, footer_height, stroke=1, fill=1)

    text_x = footer_x + 18
    text_y = footer_y + footer_height - 20
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.HexColor('#232832'))
    c.drawString(text_x, text_y, f'Certificate Verification URL: {verification_url}')
    c.drawString(text_x, text_y - 16, f'Certificate ID: {certificate_id}')
    c.drawString(text_x, text_y - 32, f'Candidate ID: {candidate_id}')
    c.drawString(text_x, text_y - 48, f'Issue Date: {interview.date.strftime("%B %d, %Y")}')
    c.drawString(text_x, text_y - 64, f'Verification No.: {verification_code}')

    qr_image = _generate_qr_image(f'{verification_url}/verify?cert={certificate_id}&candidate={candidate_id}', size=120)
    qr_reader = ImageReader(qr_image)
    qr_x = footer_x + footer_width - 140
    qr_y = footer_y + 12
    c.drawImage(qr_reader, qr_x, qr_y, width=120, height=120)
    c.setFont('Helvetica', 8)
    c.drawCentredString(qr_x + 60, qr_y - 10, 'Scan to verify')

    c.save()
    buffer.seek(0)
    return buffer
