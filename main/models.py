from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps


# Create your models here.


class Student(AbstractUser):
    enterprise = models.CharField(max_length=150, verbose_name="Предприятие")
    plot = models.CharField(max_length=150, verbose_name="Участок")
    function = models.CharField(max_length=150, verbose_name="Должность")
    surname = models.CharField(max_length=150, verbose_name="Отчество")
    student_type = models.ForeignKey(
        "main.StudentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Тип студента",
    )

    class Meta:
        db_table = "student"
        verbose_name = "Студента"
        verbose_name_plural = "Студенты"

    def __str__(self) -> str:
        return str(self.username)

    @property
    def get_available_tests(self):
        Test = apps.get_model("gtests", "Test")

        if self.student_type:
            return self.student_type.tests.all()
        return Test.objects.none()


class StudentType(models.Model):
    name = models.CharField(max_length=150, verbose_name="Тип студента")
    tests = models.ManyToManyField(
        "gtests.Test",
        blank=True,
        related_name="allowed_for_student_types",
    )
    max_attempts = models.PositiveIntegerField(
        default=1, verbose_name="Максимум попыток на тест"
    )

    class Meta:
        db_table = "Available tests"
        verbose_name = "Категория студента"
        verbose_name_plural = "Категории студентов"

    def __str__(self):
        return f"{self.name}"
