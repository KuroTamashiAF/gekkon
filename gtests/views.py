from re import S

from django.shortcuts import redirect, render

# Create your views here.
from django.template.base import kwarg_re
from django.views.generic import DetailView, FormView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from gtests.models import Test, Question, UserAnswer, UserTestResult, AnswerOption
from gtests.forms import TestForm


class TestDetailView(DetailView):
    model = Test
    template_name = "gtests/test_detail.html"
    context_object_name = "test"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['questions'] = Question.objects.all()
        return context


class TakeTestView(FormView):
    template_name = "gtests/take_test.html"
    form_class = TestForm
    # success_url = reverse_lazy("gtests:test_results", kwargs = {"test_id":test.id})

    def get_success_url(self):
        return reverse_lazy("gtests:test_results", kwargs = {"test_id":self.test.id})


    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Test, id=self.kwargs["test_id"])
        # print(self.test)
        self.questions = self.test.questions.all()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["questions"] = self.questions
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test"] = self.test
        return context

    def form_valid(self, form):
        # Сохраняем ответы пользователя
        self.save_user_answers(form.cleaned_data)
    
        # Рассчитываем и сохраняем результат
        score_data = self.calculate_score()
        print("CREATING RESULT")
        result = UserTestResult.objects.create(
            user=self.request.user,
            test=self.test,
            score=score_data["percentage"],
            total_questions=score_data["total"],
            correct_answers=score_data["correct"],
        )
        # form.save()

        messages.success(
            self.request,
            f'Тест завершён! Ваш результат: {score_data["percentage"]:.1f}%',
        )
        
        return redirect("gtests:test_results", pk=result.id)
    


    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


    def save_user_answers(self, cleaned_data):
        UserAnswer.objects.filter(
            user=self.request.user,
            question__test=self.test
        ).delete()

        answers_to_create = []

        for question in self.questions:
            # ❗ FIX: теперь это УЖЕ объект AnswerOption
            selected_option = cleaned_data.get(f"question_{question.id}")

            if not selected_option:
                continue

            answers_to_create.append(
                UserAnswer(
                    user=self.request.user,
                    question=question,
                    selected_option=selected_option,
                    is_correct=selected_option.is_correct,
                )
            )
            UserAnswer.objects.bulk_create(answers_to_create)
        
    def calculate_score(self):
        total_questions = self.questions.count()
        correct_answers = UserAnswer.objects.filter(
            user=self.request.user, question__test=self.test, is_correct=True
        ).count()

        percentage = (
            (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        )
        return {
            "correct": correct_answers,
            "total": total_questions,
            "percentage": percentage,
        }


class TestResultsView(DetailView):
    model = UserTestResult
    template_name = "gtests/test_results.html"
    context_object_name = "result"
