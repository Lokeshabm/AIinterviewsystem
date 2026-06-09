import json
import random
from pathlib import Path
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .forms import RegisterForm, ResumeUploadForm
from .models import Interview, Question, Response
from .utils import parse_resume, generate_questions_from_resume, evaluate_answer_with_ai, build_certificate


def parse_question_response_text(text):
    try:
        payload = json.loads(text)
        return payload
    except json.JSONDecodeError:
        normalized = text.replace("'", '"')
        try:
            payload = json.loads(normalized)
            return payload
        except Exception:
            data = {'technical': [], 'project': [], 'hr': []}
            lines = [line.strip(' -') for line in text.splitlines() if line.strip()]
            for line in lines:
                if line.lower().startswith('technical'):
                    current = 'technical'
                elif line.lower().startswith('project'):
                    current = 'project'
                elif line.lower().startswith('hr') or line.lower().startswith('hiring'):
                    current = 'hr'
                elif current and len(data[current]) < 5:
                    data[current].append(line)
            return data


def parse_evaluation_text(text):
    result = {'score': 0.0, 'strength': '', 'weakness': '', 'improvement': ''}
    for line in text.splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        if key == 'score':
            try:
                result['score'] = float(value.split('/')[0].strip())
            except Exception:
                result['score'] = 0.0
        elif key == 'strength':
            result['strength'] = value
        elif key == 'weakness':
            result['weakness'] = value
        elif key == 'improvement':
            result['improvement'] = value
    return result


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        print('Registering user:', username, email)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')
    return render(request, 'interview/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    next_url = request.GET.get('next') or request.POST.get('next') or None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('Attempting login:', username)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url or 'dashboard')
        messages.error(request, 'Invalid username or password')
    return render(request, 'interview/login.html', {'next_url': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    form = ResumeUploadForm()
    latest_interview = request.user.interviews.order_by('-date').first()
    return render(request, 'interview/dashboard.html', {
        'form': form,
        'latest_interview': latest_interview,
    })


@login_required
@require_POST
def upload_resume(request):
    form = ResumeUploadForm(request.POST, request.FILES)
    latest_interview = request.user.interviews.order_by('-date').first()
    if not form.is_valid():
        return render(request, 'interview/dashboard.html', {'form': form, 'latest_interview': latest_interview})
    resume_file = form.cleaned_data['resume_file']
    role = form.cleaned_data['role']
    try:
        resume_text = parse_resume(resume_file, resume_file.name)
        question_data_text = generate_questions_from_resume(resume_text, role)
        payload = parse_question_response_text(question_data_text)
        interview = Interview.objects.create(user=request.user, role=role)
        for category_name, items in payload.items():
            for item in items:
                if not item:
                    continue
                category = category_name if category_name in ['technical', 'project', 'hr'] else 'technical'
                Question.objects.create(interview=interview, text=item, category=category)
        return redirect('start_interview', interview_id=interview.id)
    except Exception as exc:
        messages.error(request, f'Unable to generate questions: {exc}')
        return redirect('dashboard')


@login_required
@require_POST
def generate_questions(request):
    return upload_resume(request)


@login_required
def start_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, user=request.user)
    questions = list(interview.questions.all())
    if not questions:
        messages.warning(request, 'No questions available yet. Upload your resume first.')
        return redirect('dashboard')
    random.shuffle(questions)
    return render(request, 'interview/interview.html', {
        'interview': interview,
        'questions': questions,
        'questions_count': len(questions),
    })


@login_required
@require_POST
def evaluate_answer(request):
    body = request.POST or request.JSON if hasattr(request, 'JSON') else request.POST
    question_id = request.POST.get('question_id')
    answer_text = request.POST.get('answer_text')
    if not question_id or not answer_text:
        return HttpResponseBadRequest('Question ID and answer text are required.')
    question = get_object_or_404(Question, id=question_id)

    try:
        evaluation_text = evaluate_answer_with_ai(question.text, answer_text)
        parsed = parse_evaluation_text(evaluation_text)
        response = Response.objects.create(
            question=question,
            answer=answer_text,
            score=parsed['score'],
            feedback=f"Strength: {parsed['strength']}\nWeakness: {parsed['weakness']}\nImprovement: {parsed['improvement']}",
        )
        return JsonResponse({
            'score': parsed['score'],
            'strength': parsed['strength'],
            'weakness': parsed['weakness'],
            'improvement': parsed['improvement'],
            'response_id': response.id,
        })
    except ValueError as e:
        return JsonResponse({
            'error': f'AI evaluation failed: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}'
        }, status=500)


@login_required
@require_POST
def save_score(request):
    interview_id = request.POST.get('interview_id')
    interview = get_object_or_404(Interview, id=interview_id, user=request.user)
    responses = Response.objects.filter(question__interview=interview)
    if not responses.exists():
        return HttpResponseBadRequest('No responses found to score.')
    total_score = sum(r.score for r in responses) / responses.count()
    interview.total_score = round(total_score, 1)
    interview.passed = interview.total_score > 7.0
    interview.save()
    return JsonResponse({'total_score': interview.total_score, 'passed': interview.passed})


@login_required
def get_certificate_ids(interview):
    year = interview.date.year
    candidate_id = f'BML-{year}-{interview.id:06d}'
    certificate_id = f'CERT-{year}-{interview.id:06d}'
    return candidate_id, certificate_id


@login_required
def view_scores(request):
    interviews = request.user.interviews.order_by('-date')
    return render(request, 'interview/scores.html', {'interviews': interviews})


@login_required
def certificate_view(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, user=request.user)
    if not interview.passed or interview.total_score is None:
        messages.error(request, 'You are not eligible to download a certificate yet.')
        return redirect('view_scores')
    candidate_id, certificate_id = get_certificate_ids(interview)
    return render(request, 'interview/certificate_preview.html', {
        'interview': interview,
        'candidate_id': candidate_id,
        'certificate_id': certificate_id,
    })


@login_required
@login_required
def download_certificate_pdf(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, user=request.user)
    if not interview.passed or interview.total_score is None:
        messages.error(request, 'You are not eligible to download a certificate yet.')
        return redirect('view_scores')
    candidate_id, certificate_id = get_certificate_ids(interview)
    pdf_buffer = build_certificate(request.user, interview, candidate_id=candidate_id, certificate_id=certificate_id)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate_{candidate_id}.pdf"'
    return response


@login_required
def import_questions_view(request):
    """View to trigger question import from generated JSON file."""
    if request.method == 'GET':
        return render(request, 'interview/import_questions.html')
    
    if request.method == 'POST':
        json_path = request.POST.get('json_path', '').strip()
        if not json_path:
            messages.error(request, 'JSON path is required.')
            return render(request, 'interview/import_questions.html')
        
        json_file = Path(json_path)
        if not json_file.exists():
            messages.error(request, f'File not found: {json_path}')
            return render(request, 'interview/import_questions.html')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except json.JSONDecodeError as e:
            messages.error(request, f'Invalid JSON: {e}')
            return render(request, 'interview/import_questions.html')
        
        if not isinstance(questions_data, list):
            messages.error(request, 'Expected JSON file to contain a list of questions.')
            return render(request, 'interview/import_questions.html')
        
        # Get or create "Question Bank" Interview
        from django.contrib.auth.models import User as DjangoUser
        from datetime import datetime
        admin_user, _ = DjangoUser.objects.get_or_create(
            username='question_bank_admin',
            defaults={'email': 'admin@questionbank.local'}
        )
        question_bank, _ = Interview.objects.get_or_create(
            user=admin_user,
            role='Question Bank',
            defaults={'date': datetime.now()}
        )
        
        created = 0
        skipped = 0
        for q_data in questions_data:
            try:
                statement = q_data.get('statement', '').strip()
                if not statement:
                    continue
                
                # Check if question already exists
                if not Question.objects.filter(text=statement).exists():
                    Question.objects.create(
                        interview=question_bank,
                        text=statement,
                        category='technical',
                    )
                    created += 1
                else:
                    skipped += 1
            except Exception:
                continue
        
        messages.success(request, f'Import complete: {created} created, {skipped} skipped.')
        return redirect('import_questions')

