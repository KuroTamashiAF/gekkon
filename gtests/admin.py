from django.contrib import admin
from gtests. models import  Test, Question, AnswerOption, UserTestResult, UserAnswer
from django.contrib import admin
from .models import UserTestAttempt

# Register your models here.

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(UserTestResult)
admin.site.register(UserAnswer)






@admin.register(UserTestAttempt)
class UserTestAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "test", "completed", "is_active", "started_at")
    list_filter = ("test", "completed", "is_active")
    search_fields = ("user__username",)

    actions = ["reset_attempts"]

    def reset_attempts(self, request, queryset):
        updated = queryset.update(is_active=False)

        self.message_user(
            request,
            f"Сброшено попыток: {updated}"
        )

    reset_attempts.short_description = "Обнулить попытки (мягко)"