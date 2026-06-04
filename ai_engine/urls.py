from django.urls import path
from . import views

urlpatterns = [
    path('note/<int:pk>/mcq/', views.GenerateMCQView.as_view(), name='generate_mcq'),
    path('note/<int:pk>/short/', views.GenerateShortQuestionsView.as_view(), name='generate_short'),
    path('note/<int:pk>/long/', views.GenerateLongQuestionsView.as_view(), name='generate_long'),
    path('note/<int:pk>/flashcards/', views.GenerateFlashcardsView.as_view(), name='generate_flashcards'),
    path('note/<int:pk>/summary/', views.GenerateSummaryView.as_view(), name='generate_summary'),
    path('note/<int:pk>/content/', views.AIGeneratedContentView.as_view(), name='ai_content'),
    path('note/<int:pk>/flashcards/pdf/', views.ExportFlashcardsPDFView.as_view(), name='flashcards_pdf'),
    path('note/<int:pk>/flashcards/study/', views.FlashcardStudyView.as_view(), name='flashcard_study'),
    path('flashcard/<int:pk>/mark/', views.MarkFlashcardLearnedView.as_view(), name='flashcard_mark'),
]
