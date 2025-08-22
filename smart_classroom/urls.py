from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main web interface
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Teachers management
    path('teacherprofiles/', views.teachers_list, name='teachers_list'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/edit/<int:teacher_id>/', views.teacher_edit, name='teacher_edit'),
    path('teachers/delete/<int:teacher_id>/', views.teacher_delete, name='teacher_delete'),

    # Assignments management (legacy - keeping for backward compatibility)
    path('assignments-old/', views.assignments_list, name='assignments_list'),
    path('assignments-old/add/', views.assignment_add, name='assignment_add'),
    path('assignments-old/edit/<int:assignment_id>/', views.assignment_edit, name='assignment_edit'),
    path('assignments-old/delete/<int:assignment_id>/', views.assignment_delete, name='assignment_delete'),

    # Quizzes management
    path('quizzes/', views.quizzes_list, name='quizzes_list'),
    path('quizzes/add/', views.quiz_add, name='quiz_add'),
    path('quizzes/edit/<int:quiz_id>/', views.quiz_edit, name='quiz_edit'),
    path('quizzes/delete/<int:quiz_id>/', views.quiz_delete, name='quiz_delete'),

    # Subjects management
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),
    path('subjects/edit/<int:subject_id>/', views.subject_edit, name='subject_edit'),
    path('subjects/delete/<int:subject_id>/', views.subject_delete, name='subject_delete'),

    # Subject Teachers management
    path('subjectteachers/', views.subject_teachers_list, name='subject_teachers_list'),
    path('subjectteachers/add/', views.subject_teacher_add, name='subject_teacher_add'),
    path('subjectteachers/edit/<int:st_id>/', views.subject_teacher_edit, name='subject_teacher_edit'),
    path('subjectteachers/delete/<int:st_id>/', views.subject_teacher_delete, name='subject_teacher_delete'),

    # Students management
    path('students/', views.students_list, name='students_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/edit/<int:student_id>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:student_id>/', views.student_delete, name='student_delete'),

    # Classrooms management
    path('classrooms/', views.classrooms_list, name='classrooms_list'),
    path('classrooms/add/', views.classroom_add, name='classroom_add'),
    path('classrooms/edit/<int:classroom_id>/', views.classroom_edit, name='classroom_edit'),
    path('classrooms/delete/<int:classroom_id>/', views.classroom_delete, name='classroom_delete'),

    # Assignment router
    path('assignments-route/', views.assignments_router, name='assignments_router'),

    # Attendance management
    path('attendance/', include(('attendance.urls', 'attendance'), namespace='attendance')),
    
    # Feedback management
    path('feedback/', include(('feedback.urls', 'feedback'), namespace='feedback')),
    
    # Grades management
    path('grades/', include(('grades.urls', 'grades'), namespace='grades')),
    
    # Assignments management
    path('assignments/', include(('assignments.urls', 'assignments'), namespace='assignments')),
    
    # Advanced Features
    path('advanced/', include(('advanced.urls', 'advanced'), namespace='advanced')),

    # User management (new comprehensive system)
    path('users/', include('users.urls')),
    
    # API paths (keeping existing API functionality)
    path('api/users/', include(('users.urls', 'users_api'), namespace='users_api')),
    path('api/classroom/', include('classroom.urls')),
    path('api/teacher/', include('teacher.urls')),
    path('api/subject/', include('subject.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
