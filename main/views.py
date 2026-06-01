from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.conf import settings
from main.forms import StudentLoginForm, StudentRegistrationForm
from django.contrib import auth, messages
from main.servises import get_available_tests_for_user, pdf_render_function
from gtests.models import Student, UserTestAttempt
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from PIL import Image as PILImage

from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from gtests.views import UserTestAttempt
from urllib.parse import quote
import re
import logging
import datetime as dt

# Create your views here.


logger = logging.getLogger("main")


class StudentLoginView(LoginView):
    template_name = "main/login.html"
    form_class = StudentLoginForm
    login_url = "main:login"
    success_url = reverse_lazy("main:index")

    def form_valid(self, form):
        user = form.get_user()
        if user:
            auth.login(self.request, user)
            logger.info(f"LOGIN {user.username}-{dt.datetime.now()}")
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
            context["is_superuser"] = user.is_superuser
            context["username"] = user.username
            context["is_staff"] = user.is_staff
        return context

    def form_valid(self, form):
        user = form.instance
        if user:
            form.save()
            # print("Данные записаны")
            messages.success(self.request, "Данные сохранены")
            logger.info(f"REGISTRATION SUCCES | {user.username}-{dt.datetime.now()}")

        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):

        messages.error(self.request, "Данные не сохранены")
        logger.info(f"REGISTRATION FAIL | {user.username}-{dt.datetime.now()}")

        return HttpResponseRedirect(self.success_url)


class AdminStudentsView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "main/look_student.html"
    context_object_name = "students"

    def get_context_data(self, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            context = super().get_context_data(**kwargs)
            context["title"] = "Геккон тестирование - Выбор студента"
            context["is_superuser"] = user.is_superuser
            context["username"] = user.username
            context["is_staff"] = user.is_staff

        return context


class StudentProfileView(LoginRequiredMixin, TemplateView):
    template_name = "main/student_profile.html"

    def get_context_data(self, **kwargs) -> dict[str]:
        st_id = self.kwargs.get("st_id")
        student = get_object_or_404(Student, id=st_id)
        user = self.request.user

        context = super().get_context_data(**kwargs)
        context["title"] = "Геккон тестирование - Профиль студента"
        context["is_superuser"] = user.is_superuser
        context["username"] = user.username
        context["is_staff"] = user.is_staff
        context["student"] = student
        context["attempts"] = (
            UserTestAttempt.objects.filter(user=student, completed=True)
            .select_related("test")
            .order_by("-started_at")
        )
        return context


class StudentTestResultView(LoginRequiredMixin, DetailView):
    model = UserTestAttempt
    template_name = "main/student_test_result.html"
    context_object_name = "attempt"

    def get_queryset(self):

        return UserTestAttempt.objects.select_related("user", "test").prefetch_related(
            "answers__question",
            "answers__selected_option",
            "answers__question__options",
        )

    def get_context_data(self, **kwargs):
        test = self.get_object().test
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["title"] = "Геккон тестирование - Результаты тестов студентов"
        context["username"] = user.username
        context["is_staff"] = user.is_staff
        context["is_superuser"] = user.is_superuser
        context["test"] = test
        logger.info(f"RESULT VIEW | {user.username}-{dt.datetime.now()}")
        return context


@login_required
def logout(request):
    auth.logout(request)
    return redirect("main:login")


def export_attempt_excel(request, pk):
    try:
        attempt = get_object_or_404(
            UserTestAttempt.objects.select_related("user", "test").prefetch_related(
                "answers__question",
                "answers__selected_option",
                "answers__question__options",
            ),
            pk=pk,
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Result"

        ws.append(
            [
                "Студент",
                "Тест",
                "Процент",
                "Вопрос",
                "Выбранный ответ",
                "Правильный ответ",
                "Результат",
                "Изображение",
            ]
        )

        score = attempt.result.score if hasattr(attempt, "result") else 0

        row_num = 2

        for answer in attempt.answers.all():
            correct_option = answer.question.options.filter(is_correct=True).first()

            ws.append(
                [
                    str(attempt.user),
                    str(attempt.test),
                    score,
                    answer.question.text,
                    (
                        answer.selected_option.text
                        if answer.selected_option
                        else "Не ответил"
                    ),
                    correct_option.text if correct_option else "",
                    "Верно" if answer.is_correct else "Неверно",
                    "",
                ]
            )

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
                    print(e)

            row_num += 1

        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 10
        ws.column_dimensions["D"].width = 50
        ws.column_dimensions["E"].width = 30
        ws.column_dimensions["F"].width = 30
        ws.column_dimensions["G"].width = 15
        ws.column_dimensions["H"].width = 20

        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        filename = f"{attempt.user.first_name}_{attempt.user.last_name}_{attempt.user.surname}_{attempt.test.title}"
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        filename = filename.replace(" ", "_")

        response["Content-Disposition"] = (
            f"attachment; filename*=UTF-8''{quote(filename)}.xlsx"
        )

        wb.save(response)

        logger.info(f"EXCEL EXPORT | {request.user.username}-{dt.datetime.now()}")
        return response

    except Exception as e:
        logger.exception(
            f"ERROR EXCEL EXPORT {request.user.username}--{dt.datetime.now()}"
        )
        logger.exception(f"{e}")

        return redirect("main:index")


def pdf_export_result(request, pk):
    return pdf_render_function(request, pk)


    # try:
    #     attempt = get_object_or_404(UserTestAttempt, pk=pk)

    #     packet = BytesIO()  # СОЗДАЁМ PDF В ПАМЯТИ

    #     pdfmetrics.registerFont(
    #         TTFont("DejaVu", settings.BASE_DIR / "static" / "fonts" / "DejaVuSans.ttf")
    #     )


    #     can = canvas.Canvas(packet, pagesize=A4)
    #     user = attempt.user

    #     full_name = f"{user.last_name} {user.first_name} {user.surname}"

    #     can.setFont("DejaVu", 12)  # ВСТАВКА ТЕКСТА В PDF  X Y координаты
    #     can.drawString(100, 700, f"ФИО: {full_name}")
    #     can.drawString(100, 680, f"Должность: {user.function}")
    #     can.drawString(100, 660, f"Предприятие: {user.enterprise}")
    #     can.drawString(100, 640, f"Участок: {user.plot}")

    #     can.drawString(100, 620, f"Дата теста: {attempt.started_at.strftime('%d.%m.%Y')}")

    #     correct = attempt.answers.filter(is_correct=True).count()
    #     total = attempt.answers.count()
    #     percentage = (correct / total * 100) if total > 0 else 0

    #     can.drawString(100, 600, f"Процент правильных ответов: {percentage:.1f}%")

    #     y = 550

    #     for answer in attempt.answers.all():

    #         text = f"{answer.question.text[:50]} | " f"Ответ: " f"{answer.selected_option}"

    #         can.drawString(50, y, text)
    #         y -= 20

    #     can.save()

    #     # ==========================================
    #     # ПЕРЕХОД В НАЧАЛО BUFFER
    #     # ==========================================

    #     packet.seek(0)

    #     # ==========================================
    #     # ЧИТАЕМ TEMPLATE PDF
    #     # ==========================================

    #     template_path = settings.BASE_DIR / "static" / "pdf" / "template.pdf"

    #     template_pdf = PdfReader(open(template_path, "rb"))

    #     overlay_pdf = PdfReader(packet)

    #     output = PdfWriter()

    #     # ==========================================
    #     # ПЕРВАЯ СТРАНИЦА
    #     # ==========================================

    #     page = template_pdf.pages[0]

    #     page.merge_page(overlay_pdf.pages[0])

    #     output.add_page(page)

    #     # ==========================================
    #     # ОТДАЁМ PDF
    #     # ==========================================

    #     response = HttpResponse(content_type="application/pdf")

    #     # filename = f"{user.last_name}_{attempt.test.title}.pdf"

    #     filename = f"{attempt.user.last_name}_{attempt.user.first_name}_{attempt.user.surname}_{attempt.test.title}.pdf"
    #     filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    #     filename = filename.replace(" ", "_")

    #     response["Content-Disposition"] = f'attachment; filename="{filename}"'

    #     output.write(response)

    #     logger.info(f"PDF EXPORT {request.user.username}-{dt.datetime.now()}")
    #     return response
    
    # except Exception as e:
    #     logger.exception(f"ERROR PDF EXPORT {request.user.username}-{dt.datetime.now()}")
    #     logger.exception(f"{e}")



