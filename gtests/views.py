from django.shortcuts import redirect
from django.views.generic import DetailView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from gtests.models import Test, UserAnswer, UserTestResult, UserTestAttempt
from gtests.forms import TestForm
from main.servises import get_available_tests_for_user
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class TestDetailView(DetailView):
    model = Test
    template_name = "gtests/test_detail.html"
    context_object_name = "test"

    def get_queryset(self):
        return get_available_tests_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Начало Теста "
        context["is_staff"] = self.request.user.is_staff
        context["is_superuser"] = self.request.user.is_superuser
        context["username"] = self.request.user.username
        return context


class TakeTestView(FormView):
    template_name = "gtests/take_test.html"
    form_class = TestForm

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Test, id=self.kwargs["test_id"])

        # ✅ Проверка доступа
        allowed_tests = get_available_tests_for_user(request.user)
        if self.test not in allowed_tests:
            raise PermissionDenied()

        # ✅ Получаем или создаём попытку
        self.attempt, _ = UserTestAttempt.objects.get_or_create(
            user=request.user,
            test=self.test,
        )

        # 🚫 Если тест уже завершён
        if self.attempt.completed:
            return redirect("main:home")

        self.questions = list(self.test.questions.all())

        # ✅ текущий вопрос
        answered_count = self.attempt.answers.count()

        try:
            self.q_index = int(request.GET.get("q", answered_count))
        except:
            self.q_index = answered_count

        # 🚫 запрет назад / вперёд
        if self.q_index != answered_count:
            return redirect(f"{request.path}?q={answered_count}")

        # 🚫 если всё отвечено — завершаем
        if answered_count >= len(self.questions):
            return self.finish_test()

        self.current_question = self.questions[self.q_index]

        return super().dispatch(request, *args, **kwargs)

    # def get_success_url(self):
    #     return reverse_lazy("gtests:test_results", kwargs={"test_id": self.test.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["questions"] = [self.current_question]
        return kwargs



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test"] = self.test
        context["question"] = self.current_question
        context["q_index"] = self.q_index
        context["total"] = len(self.questions)
        context["title"] = "Геккон тестирование - Тест"
        context["is_staff"] = self.request.user.is_staff
        context["is_superuser"] = self.request.user.is_superuser
        context["username"] = self.request.user.username
        # context["form_questions"] = zip(self.get_form(), self.questions)
        return context

    def form_valid(self, form):
        selected_option = form.cleaned_data.get(
            f"question_{self.current_question.id}"
        )

        if selected_option:
            UserAnswer.objects.create(
                user=self.request.user,
                attempt=self.attempt,
                question=self.current_question,
                selected_option=selected_option,
                is_correct=selected_option.is_correct,
            )

        return redirect(f"{self.request.path}?q={self.q_index + 1}")



    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def save_user_answers(self, cleaned_data):
        question = self.current_question

        selected_option = cleaned_data.get(f"question_{question.id}")

        if not selected_option:
            return

        UserAnswer.objects.update_or_create(
            user=self.request.user,
            question=question,
            defaults={
                "selected_option": selected_option,
                "is_correct": selected_option.is_correct,
            },
        )


    def finish_test(self):
        total = self.attempt.answers.count()
        correct = self.attempt.answers.filter(is_correct=True).count()

        percentage = (correct / total * 100) if total > 0 else 0

        result = UserTestResult.objects.create(
            attempt=self.attempt,
            score=percentage,
            total_questions=total,
            correct_answers=correct,
        )

        self.attempt.completed = True
        self.attempt.save()

        messages.success(
            self.request,
            f"Тест завершён! Результат: {percentage:.1f}%"
        )

        return redirect("gtests:test_results", pk=result.id)


    # def calculate_score(self):
    #     total_questions = len(self.questions)
    #     correct_answers = UserAnswer.objects.filter(
    #         user=self.request.user, question__test=self.test, is_correct=True
    #     ).count()

    #     percentage = (
    #         (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    #     )
    #     return {
    #         "correct": correct_answers,
    #         "total": total_questions,
    #         "percentage": percentage,
    #     }

@method_decorator(never_cache, name="dispatch")
class TestResultsView(DetailView):
    model = UserTestResult
    template_name = "gtests/test_results.html"
    context_object_name = "result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.object

        user_answers  = result.attempt.answers.select_related(
    "question", "selected_option"
)

        context["username"] = self.request.user.username
        context["user_answers"] = user_answers
        context["is_staff"] = self.request.user.is_staff
        context["is_superuser"] = self.request.user.is_superuser

        return context
