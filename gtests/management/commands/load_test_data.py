import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from gtests.models import Test, Question, AnswerOption


class Command(BaseCommand):
    help = "Загрузка тестов из JSON"
    def handle(self, *args, **kwargs):

        file_names = os.listdir(os.path.join(settings.BASE_DIR / "for_tests_json"))
        count_tests = 0


        for file_name in file_names:

            file_path = os.path.join(settings.BASE_DIR / "for_tests_json" , file_name)


            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR("Файл не найден"))
                return

            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            # создаём тест
            
            
            test = Test.objects.create(
            title=data["tests_title"],
            description=data["test_description"]
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
            count_tests+=1

        self.stdout.write(self.style.SUCCESS(f"Тесты успешно загружены!= {count_tests}"))