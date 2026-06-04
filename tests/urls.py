from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateTestView.as_view(), name='create_test'),
    path('<int:pk>/', views.TakeTestView.as_view(), name='take_test'),
    path('<int:pk>/submit/', views.SubmitTestView.as_view(), name='submit_test'),
    path('result/<int:pk>/', views.TestResultView.as_view(), name='test_result'),
    path('', views.TestHistoryView.as_view(), name='test_history'),
]
