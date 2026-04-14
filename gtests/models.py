from django.db import models
from main.models import Student


# Create your models here.
class TestCategories(models.Model):
    name = models.CharField(
        max_length=150, unique=True, verbose_name="Название категории"
    )

    class Meta:
        db_table = "category"
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"
        ordering = ("id",)

    def __str__(self):
        return str(self.name)


class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit = models.IntegerField(help_text="Время в минутах", null=True, blank=True)
    image  = models.ImageField(upload_to="tests_images/", blank=True, null=True, verbose_name="Изображение")

    class Meta:
        db_table = "test"
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return str(self.title)


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    image = image = models.ImageField(
        upload_to="question_images/", blank=True, null=True, verbose_name="Изображение", default="question_images/plug.jpg")

    class Meta:
        db_table = "Question"
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "AnswerOption"
        verbose_name = "Опции ответа"
        verbose_name_plural = "Опции ответов"


    def __str__(self):
        return f"{self.text}"
    


class UserTestResult(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "UserTestResult"
        verbose_name = "Результаты теста"
        verbose_name_plural = "Результаты тестов"


class UserAnswer(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    class Meta:
        db_table = "UserAnswer"
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответ пользователя"
