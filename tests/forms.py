from django import forms
from .models import PracticeTest


class PracticeTestForm(forms.ModelForm):
    class Meta:
        model = PracticeTest
        fields = ['title', 'difficulty', 'question_count', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Biology Chapter 5 Quiz', 'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'question_count': forms.NumberInput(attrs={'min': 1, 'max': 50, 'placeholder': '10', 'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 1, 'max': 180, 'placeholder': '30', 'class': 'form-control'}),
        }
        labels = {
            'title': 'Test Title',
            'difficulty': 'Difficulty Level',
            'question_count': 'Number of Questions',
            'duration_minutes': 'Time Limit',
        }
        help_texts = {
            'question_count': 'How many questions to include in this test',
            'duration_minutes': 'In minutes',
        }
