from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('subject/<int:pk>/follow/', views.ToggleFollowSubjectView.as_view(), name='toggle_follow_subject'),
    path('password/reset/direct/', views.DirectPasswordResetView.as_view(), name='direct_password_reset'),
]
