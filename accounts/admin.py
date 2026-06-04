from django.contrib import admin
from django.utils.html import format_html
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'avatar_preview', 'ai_generations_used', 'uploads_today', 'created_at']
    list_filter = ['plan', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['avatar_preview', 'ai_generations_used', 'uploads_today', 'created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': ['user', 'plan', 'avatar', 'avatar_url', 'avatar_preview', 'bio']}),
        ('Usage', {'fields': ['ai_generations_used', 'uploads_today', 'created_at', 'updated_at']}),
    ]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width:50px;height:50px;border-radius:50%;object-fit:cover">', obj.avatar.url)
        if obj.avatar_url:
            return format_html('<img src="{}" style="width:50px;height:50px;border-radius:50%;object-fit:cover">', obj.avatar_url)
        return '-'
    avatar_preview.short_description = 'Avatar'
