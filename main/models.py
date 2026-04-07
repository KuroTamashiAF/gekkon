from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class Student(AbstractUser):
    enterprise = models.CharField(max_length=150, verbose_name="Предприятие")
    plot = models.CharField(max_length=150, verbose_name="Участок")
    function = models.CharField(max_length=150, verbose_name="Должность")
    surname = models.CharField(max_length=150, verbose_name="Отчество")

    class Meta:
        db_table = "student"
        verbose_name = "Студента"
        verbose_name_plural = "Студенты"

    def __str__(self) -> str:
        return str(self.username)
