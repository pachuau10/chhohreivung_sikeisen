from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('advertise/', views.AdvertiseView.as_view(), name='advertise'),
    path('community/', views.CommunityView.as_view(), name='community'),
    path('community/post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('community/post/<int:pk>/like/', views.PostLikeToggleView.as_view(), name='post_like'),
    path('community/post/<int:pk>/comment/', views.PostCommentAddView.as_view(), name='post_comment'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('pricing/create-order/', views.CreateOrderView.as_view(), name='create_order'),
    path('pricing/verify-payment/', views.VerifyPaymentView.as_view(), name='verify_payment'),
    path('pricing/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('notifications/', views.NotificationPageView.as_view(), name='notifications'),
    path('notifications/api/', views.NotificationListView.as_view(), name='notifications_api'),
    path('notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='notification_read'),
    path('notifications/read-all/', views.MarkAllNotificationsReadView.as_view(), name='notifications_read_all'),
]
