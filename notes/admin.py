from django.contrib import admin
from .models import Subject, Note, Bookmark, Like, Download, Comment, Post, PostComment, PostLike


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'subject', 'visibility', 'download_count', 'like_count', 'is_processed', 'created_at']
    list_filter = ['visibility', 'is_processed', 'subject', 'created_at']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['extracted_text', 'download_count', 'like_count', 'bookmark_count', 'page_count', 'file_type']
    actions = ['delete_selected']

    def delete_notes(self, request, queryset):
        for note in queryset:
            note.file.delete()
            note.delete()
        self.message_user(request, f'{queryset.count()} notes deleted.')
    delete_notes.short_description = 'Delete selected notes permanently'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'created_at']
    list_filter = ['created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'created_at']
    list_filter = ['created_at']


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'created_at']
    list_filter = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'image', 'shared_note', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
