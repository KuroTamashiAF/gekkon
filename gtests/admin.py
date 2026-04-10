from django.contrib import admin
from gtests. models import TestCategories, Test, Question, AnswerOption, UserTestResult, UserAnswer

# Register your models here.
admin.site.register(TestCategories)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(UserTestResult)
admin.site.register(UserAnswer)
