from django.conf import settings
from django.conf.urls.static import static


# 
# URL configuration for HenkonKnowledgeTest project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
#

app_name = "main"

from django.urls import path

from main import views

urlpatterns = [
    path("", views.StudentLoginView.as_view(), name="login"),
    path("index/", views.IndexView.as_view(), name="index"),
    path("result_student/",views.AdminStudentsView.as_view(), name="result_student"),
    path("student_profile/<int:st_id>/",views.StudentProfileView.as_view(), name="student_profile"),
    path("registration/", views.RegistrationStudentView.as_view(), name="registration"),
    path("student_result/<int:pk>/", views.StudentTestResultView.as_view(), name="student_result"),
    path("attempt/<int:pk>/export-excel/",views.export_attempt_excel, name="export_attempt_excel"),
    path("attempt/<int:pk>/export-pdf/",views.pdf_export_result, name="export_attempt_pdf"),
    path("logout/", views.logout, name="logout"),
    path('test-400/', views.test_400, name='test_400'),
    path('test-403/', views.test_403, name='test_403'),
    path('test-404/', views.test_404, name='test_404'),
    path('test-500/', views.test_500, name='test_500'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
