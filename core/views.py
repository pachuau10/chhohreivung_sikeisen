from itertools import chain
from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone as tz
from datetime import timedelta, date as date_class
from django.db.models import Count, Q, Prefetch, F, Value, CharField
from django.db.models.functions import Substr
from notes.models import Note, Comment, Post, PostLike, PostComment
from notes.forms import PostForm
from core.forms import ContactForm
from ai_engine.models import GeneratedQuestion, Flashcard, Summary
from tests.models import PracticeAttempt


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_notes_count'] = Note.objects.filter(visibility='public').count()
        context['recent_notes'] = Note.objects.filter(visibility='public', extracted_text__gt='').select_related('user', 'subject').annotate(preview=Substr('extracted_text', 1, 200))[:6]
        context['community_posts'] = Post.objects.filter(shared_note__visibility='public').select_related('user', 'shared_note').order_by('-created_at')[:6]
        from ai_engine.models import Summary
        note_ids = [p.shared_note_id for p in context['community_posts'] if p.shared_note_id]
        if note_ids:
            summaries = {}
            for s in Summary.objects.filter(note_id__in=note_ids).order_by('-created_at'):
                if s.note_id not in summaries:
                    summaries[s.note_id] = s.content[:200] + ('...' if len(s.content) > 200 else '')
            for p in context['community_posts']:
                if p.shared_note_id and p.shared_note_id in summaries:
                    p.shared_summary = summaries[p.shared_note_id]
        return context


class CommunityView(LoginRequiredMixin, TemplateView):
    template_name = 'core/community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from django.core.paginator import Paginator
        posts_qs = Post.objects.all().select_related('user', 'shared_note').only('id', 'user', 'content', 'image', 'shared_note', 'like_count', 'created_at').prefetch_related(
            Prefetch('comments', queryset=PostComment.objects.select_related('user').only('id', 'user', 'post', 'content', 'created_at').order_by('created_at')),
        ).annotate(comment_count=Count('comments')).order_by('-created_at')

        paginator = Paginator(posts_qs, 10)
        page = paginator.get_page(self.request.GET.get('page'))
        context['items'] = page.object_list
        context['page_obj'] = page

        note_ids = [p.shared_note_id for p in page.object_list if p.shared_note_id]
        if note_ids:
            summaries = {s.note_id: (s.content[:200] + ('...' if len(s.content) > 200 else '')) for s in Summary.objects.filter(note_id__in=note_ids).order_by('-created_at')}
            for p in page.object_list:
                if p.shared_note_id and p.shared_note_id in summaries:
                    p.shared_summary = summaries[p.shared_note_id]

        context['post_liked_ids'] = set(user.post_likes.values_list('post_id', flat=True))
        context['generations_remaining'] = user.profile.generations_remaining
        context['uploads_remaining'] = user.profile.uploads_remaining
        context['plan'] = user.profile.plan
        context['post_form'] = PostForm(user=user)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('community')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostLikeToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        deleted, _ = PostLike.objects.filter(user=request.user, post_id=pk).delete()
        if deleted:
            Post.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
            count = Post.objects.values_list('like_count', flat=True).get(pk=pk)
            return JsonResponse({'liked': False, 'count': count})
        post = Post.objects.only('user_id', 'content').get(pk=pk)
        PostLike.objects.create(user=request.user, post_id=pk)
        Post.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
        if post.user_id != request.user.pk:
            user = User.objects.get(pk=post.user_id)
            create_notification(user, 'like', f'{request.user.username} liked your post', f'"{post.content[:80]}"', f'/community/')
        count = Post.objects.values_list('like_count', flat=True).get(pk=pk)
        return JsonResponse({'liked': True, 'count': count})


class PostCommentAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if not request.user.is_staff and request.user.profile.plan == 'free':
            return JsonResponse({'error': 'Commenting requires Premium. Upgrade to join the conversation.'}, status=403)
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)
        comment = PostComment.objects.create(post=post, user=request.user, content=content)
        if post.user != request.user:
            create_notification(post.user, 'comment', f'{request.user.username} replied to your post', f'"{content[:80]}"', f'/community/')
        return JsonResponse({
            'success': True,
            'id': comment.id,
            'user': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'avatar': comment.user.profile.avatar.url if comment.user.profile.avatar else (comment.user.profile.avatar_url or ''),
        })


from django.utils import timezone
from core.models import ContactMessage, PageVisit, Earning, Subscription, Notification
from accounts.models import Profile
from notes.models import Download


def create_notification(user, ntype, title, message, link=''):
    Notification.objects.create(user=user, notification_type=ntype, title=title, message=message, link=link)


class NotificationPageView(LoginRequiredMixin, TemplateView):
    template_name = 'core/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(user=self.request.user)[:50]
        context['unread_count'] = Notification.objects.filter(user=self.request.user, is_read=False).count()
        return context


class NotificationListView(LoginRequiredMixin, View):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:20]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        data = [{
            'id': n.id, 'type': n.notification_type, 'title': n.title, 'message': n.message,
            'link': n.link, 'is_read': n.is_read, 'created_at': n.created_at.isoformat(),
        } for n in notifications]
        return JsonResponse({'notifications': data, 'unread_count': unread_count})


class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Notification, pk=pk, user=request.user)
        note.is_read = True
        note.save(update_fields=['is_read'])
        return JsonResponse({'success': True})


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})


class SupportView(TemplateView):
    template_name = 'core/support.html'


class AboutView(TemplateView):
    template_name = 'core/about.html'


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        cd = form.cleaned_data
        ContactMessage.objects.create(name=cd['name'], email=cd['email'], subject=cd['subject'], message=cd['message'])
        try:
            send_mail(
                f'Contact: {cd["subject"]}',
                f'From: {cd["name"]} ({cd["email"]})\n\n{cd["message"]}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(self.request, 'Message sent! We\'ll get back to you soon.')
        return super().form_valid(form)


class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    template_name = 'core/terms.html'


class AdvertiseView(TemplateView):
    template_name = 'core/advertise.html'


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['total_users'] = User.objects.count()
        context['users_today'] = User.objects.filter(date_joined__date=today).count()
        context['total_notes'] = Note.objects.count()
        context['notes_today'] = Note.objects.filter(created_at__date=today).count()
        context['total_questions'] = GeneratedQuestion.objects.count()
        context['total_flashcards'] = Flashcard.objects.count()
        context['total_tests'] = PracticeAttempt.objects.count()
        context['total_posts'] = Post.objects.count()
        context['total_comments'] = PostComment.objects.count()
        context['total_contact'] = ContactMessage.objects.count()
        context['unread_contact'] = ContactMessage.objects.filter(is_read=False).count()
        context['plan_counts'] = {
            'free': Profile.objects.filter(plan='free').count(),
            'premium': Profile.objects.filter(plan='premium').count(),
            'pro': Profile.objects.filter(plan='pro').count(),
        }
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_notes'] = Note.objects.select_related('user').order_by('-created_at')[:5]
        context['recent_contact'] = ContactMessage.objects.filter(is_read=False)[:5]
        context['total_downloads'] = Download.objects.count()
        context['total_earnings'] = sum(e.amount for e in Earning.objects.all())
        context['earnings_this_month'] = sum(e.amount for e in Earning.objects.filter(date__year=today.year, date__month=today.month))
        context['unique_visits_today'] = PageVisit.unique_visits_today()
        context['unique_visits_all'] = PageVisit.unique_visits_all()
        context['top_pages'] = PageVisit.top_pages()
        return context


class PricingView(TemplateView):
    template_name = 'core/pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_plan'] = self.request.user.profile.plan
            context['has_active_subscription'] = Subscription.objects.filter(
                user=self.request.user, status='active'
            ).exists()
        context['razorpay_key_id'] = settings.RAZORPAY_KEY_ID
        return context


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        import razorpay
        plan = request.POST.get('plan', '')
        if plan not in ['premium']:
            return JsonResponse({'error': 'Invalid plan'}, status=400)
        amount = settings.PLAN_PRICES.get(plan)
        if not amount:
            return JsonResponse({'error': 'Plan not found'}, status=400)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'receipt': f'{request.user.id}_{tz.now().timestamp()}',
            'notes': {'plan': plan, 'user_id': str(request.user.id)},
        })
        Subscription.objects.create(
            user=request.user,
            plan=plan,
            razorpay_order_id=order['id'],
            amount=amount / 100,
            status='active',
        )
        return JsonResponse({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'name': 'Chhohreivung',
            'description': f'{plan.title()} Plan',
            'prefill_email': request.user.email,
            'prefill_name': request.user.get_full_name() or request.user.username,
        })


class VerifyPaymentView(LoginRequiredMixin, View):
    def post(self, request):
        import razorpay
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            client.utility.verify_payment_signature(params)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success': False, 'error': 'Signature verification failed'})
        sub = Subscription.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if sub:
            sub.razorpay_payment_id = razorpay_payment_id
            sub.status = 'active'
            sub.start_date = tz.now()
            sub.end_date = tz.now() + timedelta(days=30)
            sub.save()
            profile = request.user.profile
            profile.plan = sub.plan
            profile.save()
            try:
                send_mail(
                    'Payment Successful — Chhohreivung Premium',
                    f'Hi {request.user.username},\n\nYour payment of ₹{sub.amount} for the {sub.plan.title()} plan was successful.\n\nYour plan is now active. Thank you for upgrading!\n\n— Chhohreivung Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        return JsonResponse({'success': True, 'plan': sub.plan if sub else 'premium'})


@csrf_exempt
def razorpay_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    import razorpay
    import json
    data = json.loads(request.body)
    event = data.get('event', '')
    if event == 'payment.captured':
        payload = data.get('payload', {}).get('payment', {}).get('entity', {})
        order_id = payload.get('order_id', '')
        payment_id = payload.get('id', '')
        sub = Subscription.objects.filter(razorpay_order_id=order_id).first()
        if sub and not sub.razorpay_payment_id:
            sub.razorpay_payment_id = payment_id
            sub.status = 'active'
            sub.start_date = tz.now()
            sub.end_date = tz.now() + timedelta(days=30)
            sub.save()
            profile = sub.user.profile
            profile.plan = sub.plan
            profile.save()
    return HttpResponse(status=200)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        hour = tz.localtime(tz.now()).hour
        if hour < 12:
            context['time_greeting'] = 'Good Morning'
        elif hour < 17:
            context['time_greeting'] = 'Good Afternoon'
        else:
            context['time_greeting'] = 'Good Evening'
        context['uploaded_notes'] = Note.objects.filter(user=user).count()
        context['downloads'] = user.downloads.count()
        context['saved_notes'] = user.bookmarks.count()
        context['generated_content'] = GeneratedQuestion.objects.filter(user=user).count()
        context['flashcards'] = Flashcard.objects.filter(user=user).count()
        context['test_attempts'] = PracticeAttempt.objects.filter(user=user).count()
        context['recent_notes'] = Note.objects.filter(user=user).select_related('subject')[:5]
        context['recent_tests'] = PracticeAttempt.objects.filter(user=user).select_related('test')[:5]
        today = date_class.today()
        profile = user.profile
        if profile.last_streak_date != today:
            if profile.last_streak_date == today - timedelta(days=1):
                profile.login_streak += 1
            else:
                profile.login_streak = 1
            profile.last_streak_date = today
            profile.save(update_fields=['login_streak', 'last_streak_date'])
        context['streak'] = profile.login_streak
        context['generations_remaining'] = user.profile.generations_remaining
        context['uploads_remaining'] = user.profile.uploads_remaining
        context['plan'] = user.profile.plan
        context['limits'] = user.profile._get_limits()
        followed_ids = user.profile.followed_subjects.values_list('pk', flat=True)
        context['followed_subject_notes'] = Note.objects.filter(visibility='public', subject_id__in=followed_ids).exclude(user=user).select_related('user', 'subject')[:8]
        context['followed_subjects'] = user.profile.followed_subjects.all()
        return context
