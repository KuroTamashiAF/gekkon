from django.shortcuts import redirect
from django.views.generic import DetailView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from main.servises import get_available_tests_for_user
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from datetime import timedelta
from gtests.services import word_ending
from gtests.models import Test, UserAnswer, UserTestResult, UserTestAttempt
from gtests.forms import TestForm
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment
from PIL import Image as PILImage 


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
        context["min_ending"] = word_ending(int(self.get_object().time_limit))
    
        
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

        attempts_count = UserTestAttempt.objects.filter(
            user=request.user,
            test=self.test,
            completed=True,
            is_active=True,
        ).count()

        max_attempts = getattr(request.user.student_type, "max_attempts", 1)

        if attempts_count >= max_attempts:
            messages.error(request, "Вы исчерпали количество попыток для этого теста")
            return redirect("main:index")

        # ✅ Получаем или создаём попытку

        attempt_id = request.session.get("attempt_id")

        if attempt_id:
            try:
                self.attempt = UserTestAttempt.objects.get(
                    id=attempt_id, user=request.user, test=self.test, is_active=True
                )
            except UserTestAttempt.DoesNotExist:
                self.attempt = None
        else:
            self.attempt = None

        if not self.attempt:
            self.attempt = UserTestAttempt.objects.create(
                user=request.user, test=self.test, is_active=True
            )
        request.session["attempt_id"] = self.attempt.id

        if self.test.time_limit:
            end_time = self.attempt.started_at + timedelta(minutes=self.test.time_limit)

            if timezone.now() > end_time:
                return self.finish_test()

        # 🚫 Если тест уже завершён
        if self.attempt.completed:
            return redirect("main:index")

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
        if self.test.time_limit:
            end_time = self.attempt.started_at + timedelta(minutes=self.test.time_limit)
            remaining_seconds = max(
                0,
                int((end_time - timezone.now()).total_seconds())
            )
        else:
            remaining_seconds = None

        context["remaining_seconds"] = remaining_seconds
        return context

    def form_valid(self, form):
        selected_option = form.cleaned_data.get(f"question_{self.current_question.id}")

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
        all_questions = list(self.test.questions.all())
        answered_question_ids = set(
            self.attempt.answers.values_list("question_id", flat=True)
        )
         # создаём пропущенные как "не ответил"
        for question in all_questions:
            if question.id not in answered_question_ids:
                UserAnswer.objects.create(
                    user=self.request.user,
                    attempt=self.attempt,
                    question=question,
                    selected_option=None,
                    is_correct=False,
                )
        total = len(all_questions)
        correct =  self.attempt.answers.filter(is_correct=True).count()
        percentage = (correct / total * 100) if total > 0 else 0

        result = UserTestResult.objects.create(
            user=self.request.user,
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

        self.request.session.pop("attempt_id", None)

        return redirect("gtests:test_results", pk=result.id)


        

        # total = self.attempt.answers.count()
        # correct = self.attempt.answers.filter(is_correct=True).count()

        # percentage = (correct / total * 100) if total > 0 else 0

        # result = UserTestResult.objects.create(
        #     user=self.request.user,
        #     # test = self.test,
        #     attempt=self.attempt,
        #     score=percentage,
        #     total_questions=total,
        #     correct_answers=correct,
        # )

        # self.attempt.completed = True
        # self.attempt.save()

        # messages.success(self.request, f"Тест завершён! Результат: {percentage:.1f}%")
        # self.request.session.pop("attempt_id", None)
        # return redirect("gtests:test_results", pk=result.id)


@method_decorator(never_cache, name="dispatch")
class TestResultsView(DetailView):
    model = UserTestResult
    template_name = "gtests/test_results.html"
    context_object_name = "result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.object

        user_answers = result.attempt.answers.select_related(
            "question", "selected_option"
        )

        context["username"] = self.request.user.username
        context["user_answers"] = user_answers
        context["is_staff"] = self.request.user.is_staff
        context["is_superuser"] = self.request.user.is_superuser
        context["title"] = "Геккон тестирование - Результаты"

        return context


def export_test_detailed_excel(request, tests_id):
    test = get_object_or_404(Test, id=tests_id)
    user_name = ""
    user_last_name=""
    user_surname=""

    wb = Workbook()
    ws = wb.active
    ws.title = "Detailed Results"

    headers = [
        "Пользователь",
        "Тест",
        "Процент",
        "Вопрос",
        "Выбранный ответ",
        "Правильный ответ",
        "Результат",
        "Изображение",
        "Дата",
    ]
    ws.append(headers)

    results = UserTestResult.objects.filter(
        attempt__test=test
    ).select_related("user", "attempt")
    

    row_num = 2
    

    for result in results:
        answers = UserAnswer.objects.filter(
            attempt=result.attempt
        ).select_related(
            "question",
            "selected_option"
        )
        user_name = result.user.last_name
        user_last_name = result.user.last_name
        user_surname = result.user.surname
        print(f"{user_name}_{user_last_name}_{user_surname}")

        for answer in answers:
            correct_option = answer.question.options.filter(is_correct=True).first()

            ws.append([
                str(result.user),
                str(test.title),
                result.score,
                answer.question.text,
                answer.selected_option.text if answer.selected_option else "Не ответил",
                correct_option.text if correct_option else "",
                "Верно" if answer.is_correct else "Неверно",
                "",  # сюда вставим картинку
                result.completed_at.strftime("%Y-%m-%d %H:%M"),
            ])

            # Вставка картинки
            if answer.question.image:
                try:
                    img_path = answer.question.image.path

                    pil_img = PILImage.open(img_path)
                    pil_img.thumbnail((120, 120))

                    img_bytes = BytesIO()
                    pil_img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    excel_img = ExcelImage(img_bytes)
                    ws.add_image(excel_img, f"H{row_num}")

                    ws.row_dimensions[row_num].height = 100

                except Exception as e:
                    print("Ошибка изображения:", e)

            row_num += 1

    # ширина колонок
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 50
    ws.column_dimensions["E"].width = 30
    ws.column_dimensions["F"].width = 30
    ws.column_dimensions["G"].width = 15
    ws.column_dimensions["H"].width = 20
    ws.column_dimensions["I"].width = 20

    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # filename = f"{test.title}-{results.user.last_name}-{results.user.first_name}-{results.user.surname}.xlsx"
    filename = f"{test.title}_{user_name}_{user_last_name}_{user_surname}.xlsx"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
