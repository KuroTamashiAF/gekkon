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

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    correct_answer = models.CharField(max_length=100)
    incorrect_answer_1 = models.CharField(max_length=100)
    incorrect_answer_2 = models.CharField(max_length=100)
    incorrect_answer_3 = models.CharField(max_length=100)



class UserAnswer(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)