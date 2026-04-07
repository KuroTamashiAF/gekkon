
from django import forms
from main.models import Student
from django.contrib.auth.forms import AuthenticationForm
from main.models import Student


class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Student
        fields = ["username", "password"]