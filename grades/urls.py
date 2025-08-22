from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('student/<int:student_id>/', views.student_grades, name='student_grades'),
    path('my-grades/', views.student_grades, name='my_grades'),
]