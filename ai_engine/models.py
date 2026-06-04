from django.db import models
from django.contrib.auth.models import User
from notes.models import Note


class GeneratedQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice Question'),
        ('short', 'Short Question'),
        ('long', 'Long Question'),
    ]
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='generated_questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_questions')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField()
    options = models.JSONField(blank=True, null=True, help_text='JSON array of options for MCQs')
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Generated Question'
        verbose_name_plural = 'Generated Questions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['note', 'question_type']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.get_question_type_display()} - {self.note.title}'


class Flashcard(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='flashcards')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    front = models.TextField()
    back = models.TextField()
    is_learned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['-created_at']

    def __str__(self):
        return f'Flashcard: {self.front[:50]}'


class Summary(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='summaries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='summaries')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
        ordering = ['-created_at']

    def __str__(self):
        return f'Summary: {self.note.title}'
