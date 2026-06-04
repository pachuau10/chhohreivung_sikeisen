from django.contrib import admin
from .models import GeneratedQuestion, Flashcard, Summary


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = ['note', 'user', 'question_type', 'created_at']
    list_filter = ['question_type', 'created_at']
    search_fields = ['question_text', 'note__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['note', 'user', 'is_learned', 'created_at']
    list_filter = ['is_learned', 'created_at']
    search_fields = ['front', 'back', 'note__title']


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ['note', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'note__title']
