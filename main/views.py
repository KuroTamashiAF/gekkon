from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Тестовый сервер работает"
        return context


def index(request):
    return HttpResponse("Home page sjbsjkaskvkhagscvck")
