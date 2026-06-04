from django.utils import timezone
from core.models import PageVisit


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'GET' and not request.path.startswith('/static/') and not request.path.startswith('/admin/'):
            ip = request.META.get('REMOTE_ADDR')
            session_key = request.session.session_key or ''
            if not session_key and request.user.is_authenticated:
                session_key = f'user_{request.user.id}'
            if session_key:
                PageVisit.objects.create(
                    url=request.path,
                    ip=ip,
                    session_key=session_key,
                    date=timezone.now().date(),
                )
        return response
