from django.shortcuts import redirect
from django.views.generic import DetailView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from gtests.models import Test, UserAnswer, UserTestResult
from gtests.forms import TestForm
from main.servises import get_available_tests_for_user
from django.core.exceptions import PermissionDenied


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
    # success_url = reverse_lazy("gtests:test_results", kwargs = {"test_id":test.id})

    def get_success_url(self):
        return reverse_lazy("gtests:test_results", kwargs={"test_id": self.test.id})

    def dispatch(self, request, *args, **kwargs):
        test = get_object_or_404(Test, id=self.kwargs["test_id"])
        allowed_tests = get_available_tests_for_user(request.user)

        if test not in allowed_tests:
            raise PermissionDenied("Нет доступа к этому тесту")

        self.test = test
        self.questions = list(self.test.questions.all())
        self.q_index = int(request.GET.get("q", 0)) # пагинация номер вопроса

        if self.q_index <0 or self.q_index >= len(self.questions): # пагинация проверка выхода за границы 
            self.q_index = 0
        
        self.current_question = self.questions[self.q_index]

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs["questions"] = self.questions
        kwargs["questions"] = [self.current_question]   # пагинация передаю 1 вопрос 
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
        # Сохраняем ответы пользователя
        self.save_user_answers(form.cleaned_data)
        next_q = self.q_index + 1    

        if next_q < len(self.questions):   # Пагинация если есть следующий вопрос 
            return redirect(f"{self.request.path}?q={next_q}")

        # Рассчитываем и сохраняем результат
        score_data = self.calculate_score()
        
        result = UserTestResult.objects.create(
            user=self.request.user,
            test=self.test,
            score=score_data["percentage"],
            total_questions=score_data["total"],
            correct_answers=score_data["correct"],
        )

        messages.success(
            self.request,
            f'Тест завершён! Ваш результат: {score_data["percentage"]:.1f}%',
        )

        return redirect("gtests:test_results", pk=result.id)

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

    def calculate_score(self):
        total_questions = len(self.questions)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.object

        user_answers = UserAnswer.objects.filter(
            user=result.user, question__test=result.test
        ).select_related("question", "selected_option")
        context["username"] = self.request.user.username
        context["user_answers"] = user_answers
        context["is_staff"] = self.request.user.is_staff
        context["is_superuser"] = self.request.user.is_superuser

        return context
