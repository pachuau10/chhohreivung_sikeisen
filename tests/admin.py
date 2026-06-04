from django.contrib import admin
from .models import PracticeTest, PracticeAttempt, UsageLog


@admin.register(PracticeTest)
class PracticeTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'note', 'duration_minutes', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__username']


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'total_questions', 'percentage', 'time_taken_seconds', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['user__username', 'test__title']


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'action', 'detail', 'ip_address', 'created_at']

    def has_add_permission(self, request):
        return False
