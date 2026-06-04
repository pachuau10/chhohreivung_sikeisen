from django.http import HttpResponse
from django.views.generic import View


class PlaceholderView(View):
    def get(self, request):
        return HttpResponse('Questions module integrated with ai_engine.')
