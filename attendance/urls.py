from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Main attendance list (for menu click)
    path('', views.attendance_list, name='attendance_list'),
    
    # Dashboard
    path('dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    
    # Sessions
    path('sessions/', views.attendance_sessions_list, name='attendance_sessions_list'),
    path('sessions/create/', views.attendance_session_create, name='attendance_session_create'),
    path('sessions/<int:session_id>/', views.attendance_session_detail, name='attendance_session_detail'),
    
    # AJAX endpoints
    path('mark/', views.attendance_mark_ajax, name='attendance_mark_ajax'),
    path('update-total-sessions/', views.update_total_sessions, name='update_total_sessions'),
    path('update-attendance-count/', views.update_attendance_count, name='update_attendance_count'),
    path('bulk-update-attendance-counts/', views.bulk_update_attendance_counts, name='bulk_update_attendance_counts'),
    
    # Reports
    path('reports/', views.attendance_reports, name='attendance_reports'),
    
    # Student profiles
    path('student/<int:student_id>/', views.attendance_student_profile, name='attendance_student_profile'),
]