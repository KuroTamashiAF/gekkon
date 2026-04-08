

from django import forms
from main.models import Student
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from main.models import Student


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Student
        fields = ["username", "password"]


class StudentRegistrationForm(UserCreationForm):
    class Meta():
        model = Student
        fields = [
            "password",
            "first_name",
            "last_name",
            "email",
            "enterprise",
            "plot",
            "function",
            "surname",
            ]
    password = forms.PasswordInput()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    enterprise = forms.CharField()
    plot = forms.CharField()
    function = forms.CharField()
    surname = forms.CharField()

   