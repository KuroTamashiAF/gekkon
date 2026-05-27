from django import forms
from gtests.models import Question, AnswerOption



# class TestForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         questions = kwargs.pop('questions')
#         super().__init__(*args, **kwargs)
#         for question in questions:
#             # Получаем варианты ответов для вопроса
#             options = question.options.all()
#             choices = [(str(option.id), option.text) for option in options]

#             self.fields[f'question_{question.id}'] = forms.ChoiceField(
#                 label=question.text,
#                 choices=choices,
#                 widget=forms.RadioSelect,
#                 required=True
#             )
class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions') # Получаем вопросы
        ordered_options = kwargs.pop("ordered_options",[])

        super().__init__(*args, **kwargs)

        for question in questions:
            field_name = f"question_{question.id}"
            field = forms.ModelChoiceField(
                queryset=question.options.all(),  # queryset нужен Django
                widget=forms.RadioSelect, # Radio buttons
                empty_label=None, # Убираем пустой выбор
                required=True, # Обязательный ответ
                label=question.text # Текст вопроса
            )
            field.choices = [

                # value
                # text
                (option.id, option.text)

                for option in ordered_options
            ]
            self.fields[field_name] = field

            # self.fields[f'question_{question.id}'] = forms.ModelChoiceField(
            #     queryset=question.options.all(),   # queryset вместо choices
            #     widget=forms.RadioSelect,
            #     empty_label=None,                  # убираем "пустой выбор"
            #     required=True,
            #     label=question.text
            # )