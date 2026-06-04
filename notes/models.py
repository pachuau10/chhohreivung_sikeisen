from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['name']

    def __str__(self):
        return self.name


class Comment(models.Model):
    note = models.ForeignKey('Note', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'


class Note(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/')
    file_type = models.CharField(max_length=10, editable=False)
    extracted_text = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    download_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    bookmark_count = models.IntegerField(default=0)
    page_count = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['subject', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'note']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.note.title}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='likes_rel')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'note']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} likes {self.note.title}'


class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='downloads_rel')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} downloaded {self.note.title}'


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True)
    file = models.FileField(upload_to='posts/files/', blank=True)
    file_type = models.CharField(max_length=10, blank=True, editable=False)
    extracted_text = models.TextField(blank=True)
    shared_note = models.ForeignKey('Note', on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_posts')
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'

    def process_file(self):
        if not self.file:
            return
        self.file_type = self.file.name.split('.')[-1].lower()
        try:
            import fitz
            doc = fitz.open(self.file.path)
            text = ''
            for page in doc:
                text += page.get_text()
            doc.close()
            self.extracted_text = text
        except Exception:
            try:
                import docx
                doc = docx.Document(self.file.path)
                self.extracted_text = '\n'.join(p.text for p in doc.paragraphs)
            except Exception:
                pass


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} likes post {self.post.id}'
