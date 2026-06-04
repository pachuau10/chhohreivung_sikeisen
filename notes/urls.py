from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.NoteUploadView.as_view(), name='note_upload'),
    path('<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('', views.NoteListView.as_view(), name='note_list'),
    path('<int:pk>/bookmark/', views.BookmarkToggleView.as_view(), name='toggle_bookmark'),
    path('<int:pk>/like/', views.LikeToggleView.as_view(), name='toggle_like'),
    path('<int:pk>/download/', views.NoteDownloadView.as_view(), name='download_note'),
    path('<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('<int:pk>/comment/', views.CommentAddView.as_view(), name='comment_add'),
]
