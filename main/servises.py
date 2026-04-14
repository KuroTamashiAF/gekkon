from gtests.models import Test

def get_available_tests_for_user(user):
    if not user.is_authenticated:
        return Test.objects.none()

    if not user.student_type:
        return Test.objects.none()

    return Test.objects.filter(
        allowed_for_student_types=user.student_type
    )