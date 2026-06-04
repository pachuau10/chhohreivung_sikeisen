from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Subscription(models.Model):
    PLAN_CHOICES = [('free', 'Free'), ('premium', 'Premium')]
    STATUS_CHOICES = [('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.plan} ({self.status})'


class PageVisit(models.Model):
    url = models.CharField(max_length=500)
    ip = models.GenericIPAddressField(blank=True, null=True)
    session_key = models.CharField(max_length=100, blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['session_key']),
        ]

    @classmethod
    def unique_visits_today(cls):
        return cls.objects.filter(date=timezone.now().date()).values('session_key').distinct().count()

    @classmethod
    def unique_visits_all(cls):
        return cls.objects.values('session_key').distinct().count()

    @classmethod
    def top_pages(cls, limit=5):
        from django.db.models import Count
        return cls.objects.values('url').annotate(count=Count('id', distinct=True)).order_by('-count')[:limit]


class Earning(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'${self.amount} - {self.description[:30]}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject[:40]}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('admin', 'Admin Notice'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, help_text='URL to navigate to')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'[{self.notification_type}] {self.title}'
