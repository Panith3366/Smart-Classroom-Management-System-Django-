from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'users'

urlpatterns = [
    # API endpoints
    path('api/register/', views.RegisterView.as_view(), name='api_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Web views - Authentication
    path('signup/', views.signup_view, name='signup'),
    path('student-login/', views.student_credential_login, name='student_credential_login'),
    
    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Admin user management
    path('manage/', views.user_management, name='user_management'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Role-specific views
    path('students/', views.students_list, name='students_list'),
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('student-details/', views.student_details_for_parent, name='student_details_for_parent'),
    path('student-details/<int:student_id>/', views.student_details_for_parent, name='student_details_for_parent_with_id'),
    
    # Dashboard redirects
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
]
