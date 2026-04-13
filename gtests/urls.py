from django.urls import path
from . import views


app_name = "gtests"

urlpatterns = [
    path('test/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
    path('test/take/<int:test_id>/', views.TakeTestView.as_view(), name='take_test'),
    path('results/<int:pk>/', views.TestResultsView.as_view(), name='test_results'),
]