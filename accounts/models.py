from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    avatar_url = models.URLField(blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    ai_generations_used = models.IntegerField(default=0)
    ai_generations_reset_date = models.DateField(auto_now_add=True)
    uploads_today = models.IntegerField(default=0)
    uploads_reset_date = models.DateField(auto_now_add=True)
    followed_subjects = models.ManyToManyField('notes.Subject', blank=True, related_name='followers')
    login_streak = models.IntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} Profile'

    def _get_limits(self):
        from django.conf import settings
        return settings.PLAN_LIMITS.get(self.plan, settings.PLAN_LIMITS['free'])

    @property
    def generations_remaining(self):
        from django.utils import timezone
        if self.ai_generations_reset_date != timezone.now().date():
            self.ai_generations_used = 0
            self.ai_generations_reset_date = timezone.now().date()
            self.save()
        limit = self._get_limits()['ai_generations']
        return max(0, limit - self.ai_generations_used)

    @property
    def uploads_remaining(self):
        from django.utils import timezone
        if self.uploads_reset_date != timezone.now().date():
            self.uploads_today = 0
            self.uploads_reset_date = timezone.now().date()
            self.save()
        limit = self._get_limits()['uploads']
        return max(0, limit - self.uploads_today)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
