from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('generate_questions/', views.generate_questions, name='generate_questions'),
    path('start_interview/<int:interview_id>/', views.start_interview, name='start_interview'),
    path('evaluate_answer/', views.evaluate_answer, name='evaluate_answer'),
    path('save_score/', views.save_score, name='save_score'),
    path('view_scores/', views.view_scores, name='view_scores'),
    path('certificate/<int:interview_id>/', views.certificate_view, name='certificate'),
    path('certificate/<int:interview_id>/download/', views.download_certificate_pdf, name='certificate_download'),
]
