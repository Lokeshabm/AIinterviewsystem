from django.contrib import admin
from .models import Interview, Question, Response


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date', 'total_score', 'passed')
    list_filter = ('passed', 'date')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'interview')
    list_filter = ('category',)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'score', 'timestamp')
    list_filter = ('timestamp',)
