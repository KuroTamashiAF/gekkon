import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from gtests.models import Test, Question, AnswerOption


class Command(BaseCommand):
    help = "Загрузка тестов из JSON"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "electric_test.json")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR("Файл не найден"))
            return

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # создаём тест
        test = Test.objects.create(
            title="Тест по электрике",
            description="Автоматически загружен из JSON"
        )

        for q in data["questions"]:
            question = Question.objects.create(
                test=test,
                text=q["question"],
                image=q.get("image")  # если есть
            )

            for opt in q["options"]:
                AnswerOption.objects.create(
                    question=question,
                    text=opt["text"],
                    is_correct=opt["is_correct"]
                )

        self.stdout.write(self.style.SUCCESS("Тест успешно загружен!"))