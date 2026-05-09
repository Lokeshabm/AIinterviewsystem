from django.contrib.auth.models import User
from django.db import models


class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    role = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    total_score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.role} - {self.date:%Y-%m-%d}'


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('project', 'Project'),
        ('hr', 'HR'),
    ]
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f'{self.category.title()} question for {self.interview}'


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()
    score = models.FloatField()
    feedback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response for question {self.question.id} ({self.score}/10)'
