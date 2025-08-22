from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # Role-based router for default path
    path('', views.assignments_router, name='assignments_router'),
    
    # Student views
    path('student/', views.student_assignments, name='student_assignments'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    
    # Teacher views
    path('teacher/', views.teacher_assignments, name='teacher_assignments'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
]