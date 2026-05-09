from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, min_length=8)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('That username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField()
    role = forms.CharField(max_length=255, required=True)

    def clean_resume_file(self):
        file = self.cleaned_data.get('resume_file')
        if not file:
            raise forms.ValidationError('Please upload a resume file.')
        content_type = file.content_type
        if content_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            raise forms.ValidationError('Only PDF and DOCX files are supported.')
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Resume file size must be under 5 MB.')
        return file


class AnswerForm(forms.Form):
    question_id = forms.IntegerField(widget=forms.HiddenInput)
    answer_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
