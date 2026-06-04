from django.contrib import admin
from .models import ContactMessage, PageVisit, Earning, Subscription, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ['url', 'ip', 'session_key', 'date', 'created_at']
    list_filter = ['date']
    search_fields = ['url']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'razorpay_payment_id', 'created_at']
    list_filter = ['plan', 'status', 'created_at']
    search_fields = ['user__username', 'razorpay_payment_id']


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ['amount', 'description', 'date', 'created_at']
    list_filter = ['date']
    search_fields = ['description']
