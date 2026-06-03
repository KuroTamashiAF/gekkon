from gtests.models import Test
import io  # Копирование PDF страниц
import copy  # Django settings
from django.conf import settings  # HTTP response
from django.http import HttpResponse  #
from django.shortcuts import get_object_or_404
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
)
from gtests.models import UserTestAttempt
import logging


logger  = logging.getLogger("main")


def get_available_tests_for_user(user):
    if not user.is_authenticated:
        return Test.objects.none()

    if not user.student_type:
        return Test.objects.none()

    return Test.objects.filter(allowed_for_student_types=user.student_type)


def pdf_render_function(request, pk):
    if request.user.is_authenticated:
        root_user = request.user
        try:
            attempt = get_object_or_404(UserTestAttempt, pk=pk)  # получаем попытку
            user = attempt.user  # получаем пользователя

            # Регистрируем TTF шрифт чтобы PDF понимал кириллицу

            pdfmetrics.registerFont(
                TTFont(
                    "DejaVu", settings.BASE_DIR / "static" / "fonts" / "DejaVuSans.ttf"
                )
            )

            # Создаем PDF в RAM # а не сразу в файл
            buffer = io.BytesIO()
            # СОЗДАЕМ PDF ДОКУМЕНТ
            doc = SimpleDocTemplate(
                buffer,
                # Размер страницы
                pagesize=A4,
                # # Отступ справа
                rightMargin=40,
                # # Отступ слева
                leftMargin=40,
                # # Верхний отступ
                topMargin=200,
                # # Нижний отступ
                bottomMargin=60,
            )

            elements = []  # ВСЕ ЭЛЕМЕНТЫ PDF
            styles = getSampleStyleSheet()  # СТИЛИ ТЕКСТА
            style = styles["BodyText"]  # Основной стиль
            style.fontName = "DejaVu"  # Шрифт
            style.fontSize = 10  # Размер текста
            style.leading = 14  # Межстрочный интервал
            style.alignment = TA_LEFT  # Выравнивание по левому краю

            first_page_styles = getSampleStyleSheet()
            first_page_style = first_page_styles["BodyText"]
            first_page_style.fontName = "DejaVu"
            first_page_style.fontSize = 15  # Размер текста
            first_page_style.leading = 14  # Межстрочный интервал
            first_page_style.alignment = TA_LEFT  # Выравнивание по левому краю

            response_titles = getSampleStyleSheet()
            response_title = response_titles["BodyText"]
            response_title.fontName = "DejaVu"
            response_title.fontSize = 20  # Размер текста
            response_title.leading = 14  # Межстрочный интервал
            response_title.alignment = TA_CENTER  # Выравнивание по левому краю
        



            full_name = (
                f"{user.last_name} " f"{user.first_name} " f"{user.surname}"
            )  # ФИО ПОЛЬЗОВАТЕЛЯ

            # ПОДСЧЕТ РЕЗУЛЬТАТА

            correct = attempt.answers.filter(
                is_correct=True
            ).count()  # Количество правильных ответов
            total = attempt.answers.count()  # Количество всех ответов
            percentage = (correct / total * 100) if total > 0 else 0  # Процент

            # ИНФОРМАЦИЯ О СТУДЕНТЕ

            elements.append(Paragraph(f"<b>ФИО:</b> {full_name}", first_page_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"<b>Должность</b> {user.function}",first_page_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph( f"<b>Предприятие:</b> {user.enterprise}", first_page_style ) )
            elements.append(Spacer(1, 12))
            elements.append( Paragraph( f"<b>Участок:</b> {user.plot}", first_page_style ) )
            elements.append(Spacer(1, 12))
            elements.append( Paragraph( f"<b>Дата тестирования:</b> " f"{attempt.started_at.strftime('%d.%m.%Y')}", first_page_style ) )
            elements.append(Spacer(1, 12))
            elements.append( Paragraph( f"<b>Тест:</b> " f"{attempt.test.title}", first_page_style ) )
            elements.append(Spacer(1, 12))
            elements.append( Paragraph( f"<b>Результат:</b> " f"{percentage:.1f}%", first_page_style ) )
            elements.append(Spacer(1, 100))
            elements.append(Paragraph("<b>Ответы</b>:", response_title))
            elements.append(Spacer(1, 30))


            # РАЗРЫВ СТРАНИЦЫ

            # Таблица начинается со следующей страницы
            elements.append(PageBreak())

            # ТАБЛИЦА ОТВЕТОВ
            # Заголовки таблицы

            table_data =  [[ Paragraph("<b>Вопрос</b>",style), 
                                                    Paragraph("<b>Ответ пользователя</b>", style), 
                                                    Paragraph("Результат", style) ] ]

            # ЗАПОЛНЯЕМ ТАБЛИЦУ
            for answer in attempt.answers.all():                    ## Текст вопроса
                question_text = Paragraph( answer.question.text, style )
                selected_answer = Paragraph( str(answer.selected_option) if answer.selected_option else "Нет ответа", style ) # Ответ пользователя
                result_text = Paragraph( "Верно" if answer.is_correct else "Неверно", style ) # Верно / неверно 
                table_data.append([ question_text, selected_answer, result_text ]) # Добавляем строку 

            # СОЗДАЕМ ТАБЛИЦУ
            table = Table(table_data, repeatRows=1, colWidths=[260,200,80 ])
            
            # СТИЛИ ТАБЛИЦЫ

            TableStyle([ 
                # Фон заголовка 
                ("BACKGROUND", (0, 0), (-1, 0), 
                colors.lightgrey), 
                # Шрифт 
                ("FONTNAME", (0, 0), (-1, -1), "DejaVu"), 
                # Размер текста 
                ("FONTSIZE", (0, 0), (-1, -1), 9), 
                # Выравнивание по левому краю 
                ("ALIGN", (0, 0), (-1, -1), "LEFT"), 
                # Вертикальное выравнивание 
                ("VALIGN", (0, 0), (-1, -1), "TOP"), 
                # Границы таблицы 
                ("GRID", (0, 0), (-1, -1), 1, colors.black), 
                # Левый внутренний отступ 
                ("LEFTPADDING", (0, 0), (-1, -1), 8), 
                # Правый внутренний отступ 
                ("RIGHTPADDING", (0, 0), (-1, -1), 8), 
                # Верхний внутренний отступ 
                ("TOPPADDING", (0, 0), (-1, -1), 6), 
                # Нижний внутренний отступ 
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ]) 
            
            # ДОБАВЛЯЕМ ТАБЛИЦУ

            elements.append(table)

            # ОТСТУП ПОСЛЕ ТАБЛИЦЫ
            elements.append(Spacer(1, 40))

            # ПОДПИСЬ РУКОВОДИТЕЛЯ


            # signature = Image( str( settings.BASE_DIR / "static" / "signatures" / "director_sign.png" ), width=140, height=60 )

            # БЛОК ПОДПИСИ

            # KeepTogether запрещает 
            # # разрывать подпись между страницами

            # elements.append( KeepTogether([ Paragraph( "<b>Руководитель:</b> И.Ю. Иванов", style ), Spacer(1, -35), signature ]) )


            # FOOTER


            def add_page_number(canvas, doc): 
                # Шрифт footer 
                canvas.setFont( "DejaVu", 9 ) 
                # Номер страницы 
                page_num = canvas.getPageNumber() 
                # Текст footer 
                text = f"Страница {page_num}" 
                # Рисуем справа внизу 
                canvas.drawRightString( 550, 30, text )

            # СОЗДАЕМ PDF


            doc.build( 
                elements,  # Элементы документа 
                onFirstPage=add_page_number,  # Footer первой страницы 
                onLaterPages=add_page_number, ) # Footer остальных страниц 

            # ПЕРЕХОД В НАЧАЛО BUFFER

            buffer.seek(0)

            #ЧИТАЕМ СГЕНЕРИРОВАННЫЙ PDF

            generated_pdf = PdfReader(buffer)

            #TEMPLATE PDF
            # template.pdf содержит: # логотип # колонтитулы # фирменный стиль

            template_path = ( settings.BASE_DIR / "static" / "pdf" / "template.pdf" ) 

            template_pdf = PdfReader( open(template_path, "rb") )

            # ИТОГОВЫЙ PDF

            output = PdfWriter()

            # НАКЛАДЫВАЕМ TEMPLATE # НА КАЖДУЮ СТРАНИЦУ

            for page in generated_pdf.pages: 
                template_page = copy.copy( template_pdf.pages[0] )   #Копируем template # чтобы страницы не ломались 
                template_page.merge_page(page) #    Накладываем контент 
                output.add_page(template_page) #    Добавляем страницу 

            # HTTP RESPONSE

            response = HttpResponse( content_type="application/pdf" )

            # НАЗВАНИЕ PDF

            filename = ( f"{user.last_name}_" f"{attempt.test.title}.pdf" )

            # DOWNLOAD FILE

            response[ "Content-Disposition" ] = f'attachment; filename="{filename}"'

            # СОХРАНЯЕМ PDF В RESPONSE

            output.write(response)

            # ОТДАЕМ PDF
            logger.info(f"PDF Export {root_user.username}")
            return response
        except Exception as e:
            logger.exception(e)

            return HttpResponse("Export PDF Error", status=500)
