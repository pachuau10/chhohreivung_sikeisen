from django.db import models
from django.contrib.auth.models import User
from notes.models import Note
from ai_engine.models import GeneratedQuestion


class PracticeTest(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('mixed', 'Mixed'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_tests')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='practice_tests', null=True, blank=True)
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(GeneratedQuestion, related_name='practice_tests')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='mixed')
    question_count = models.IntegerField(default=10, help_text='Number of questions to include')
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Practice Test'
        verbose_name_plural = 'Practice Tests'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PracticeAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_attempts')
    test = models.ForeignKey(PracticeTest, on_delete=models.CASCADE, related_name='attempts')
    answers = models.JSONField(default=dict, help_text='JSON of question_id: user_answer')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    time_taken_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Practice Attempt'
        verbose_name_plural = 'Practice Attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.username} - {self.test.title} ({self.percentage}%)'


class UsageLog(models.Model):
    ACTION_CHOICES = [
        ('ai_generation', 'AI Generation'),
        ('note_upload', 'Note Upload'),
        ('note_download', 'Note Download'),
        ('test_attempt', 'Test Attempt'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    detail = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usage Log'
        verbose_name_plural = 'Usage Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.get_action_display()}'
