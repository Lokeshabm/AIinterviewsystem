from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('generate/', views.generate_response, name='generate_response'),
    path('test/', views.test_page, name='test_page'),
]