import json
from django.views.generic import UpdateView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm
from notes.models import Subject


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['uploaded_notes'] = user.notes.count()
        context['downloads'] = user.downloads.count()
        context['bookmarks'] = user.bookmarks.count()
        context['followed_subjects'] = user.profile.followed_subjects.all()
        return context


class DirectPasswordResetView(TemplateView):
    template_name = 'account/direct_reset_password.html'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if not email or not password:
            return self.render_to_response(self.get_context_data(error='All fields are required.'))
        if password != password2:
            return self.render_to_response(self.get_context_data(error='Passwords do not match.', email=email))
        if len(password) < 6:
            return self.render_to_response(self.get_context_data(error='Password must be at least 6 characters.', email=email))
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully. You can now log in.')
            return redirect('account_login')
        except User.DoesNotExist:
            return self.render_to_response(self.get_context_data(error='No account found with that email.', email=email))


class ToggleFollowSubjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        profile = request.user.profile
        if profile.followed_subjects.filter(pk=subject.pk).exists():
            profile.followed_subjects.remove(subject)
            return JsonResponse({'following': False, 'message': f'Unfollowed {subject.name}'})
        profile.followed_subjects.add(subject)
        return JsonResponse({'following': True, 'message': f'Following {subject.name}'})
