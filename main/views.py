from webbrowser import get

from django.conf.global_settings import LOGIN_URL
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

# from django.contrib.auth.mixins import LoginRequiredMixin


from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from main.forms import StudentLoginForm
from main.models import Student
from django.shortcuts import get_object_or_404
from django.contrib import auth

# Create your views here.


class StudentLoginView(LoginView):
    template_name = "main/login.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("main:index")

    def form_valid(self, form):
        user = form.get_user()
        if user:
            auth.login(self.request, user)
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Авторизация"
        return context


class IndexView(TemplateView):
    template_name = "main/index.html"


    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Главная"
        context["auth"] = user.enterprise
        return context


# class RegistrationStudentView(CreateView):  # Доделать
#     template_name = "main/vartests.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Геккон тестирование - Тесты"
#         return context
