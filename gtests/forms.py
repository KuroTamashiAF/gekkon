from django import forms
from gtests.models import Question, AnswerOption



class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            # Получаем варианты ответов для вопроса
            options = question.options.all()
            choices = [(option.id, option.text) for option in options]

            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=False
            )