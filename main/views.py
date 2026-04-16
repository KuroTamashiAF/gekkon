from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from main.forms import StudentLoginForm, StudentRegistrationForm
from django.contrib import auth, messages
from main.servises import get_available_tests_for_user


# Create your views here.


class StudentLoginView(LoginView):
    template_name = "main/login.html"
    form_class = StudentLoginForm
    login_url = "main:login"
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
    

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Главная"
        if user.is_authenticated:
            context["is_superuser"] = user.is_superuser
            context["username"] = user.username
            context["is_staff"] = user.is_staff
            context["tests"] = get_available_tests_for_user(user)
            context["attemts_count"] = user.student_type.max_attempts
        return context


class RegistrationStudentView(LoginRequiredMixin, CreateView):  # Доделать
    template_name = "main/registration.html"
    form_class = StudentRegistrationForm
    success_url = reverse_lazy("main:index")

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Регистрация студента"
        if user.is_authenticated:
            context["username"] = user.username

        return context
       
    def form_valid(self, form):
        user = form.instance
        if user:
            form.save()
            print("Данные записаны")
            messages.success(self.request, "Данные сохранены")

        return HttpResponseRedirect(self.success_url)




    def form_invalid(self, form): 
    
        messages.error(self.request, "Данные не сохранены")
   
        return HttpResponseRedirect(self.success_url)



@login_required
def logout(request):
    auth.logout(request)
    return redirect("main:login")
