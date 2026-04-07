from django.http import HttpResponse, HttpResponseRedirect

# from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from main.forms import UserLoginForm

# Create your views here.


# class IndexView(TemplateView):
#     template_name = "main/index.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Геккон тестирование"
#         return context


class StudentLoginView(LoginView):
    template_name = "main/index.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("main:suc")



    def form_valid(self, form):
        user = form.get_user()
        if user:
            print("s,bhvdkhgksvkghsvkghsdghvghvkhgxszvghvshgvhgsvghvcghghcv")
            return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Авторизация"
        return context


class Succes(TemplateView):
    template_name = "main/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "УСПЕХХХХХХ"
        return context
