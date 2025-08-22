from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Main feedback list (for menu click)
    path('', views.feedback_list, name='feedback_list'),
    
    # Dashboard
    path('dashboard/', views.feedback_dashboard, name='feedback_dashboard'),
    
    # Sessions
    path('sessions/', views.feedback_sessions_list, name='feedback_sessions_list'),
    path('sessions/create/', views.feedback_session_create, name='feedback_session_create'),
    path('sessions/<int:session_id>/', views.feedback_session_detail, name='feedback_session_detail'),
    path('sessions/<int:session_id>/respond/', views.feedback_respond, name='feedback_respond'),
    
    # Templates
    path('templates/', views.feedback_templates, name='feedback_templates'),
    
    # Analytics
    path('analytics/', views.feedback_analytics, name='feedback_analytics'),
    
    # Notifications
    path('notifications/', views.feedback_notifications, name='feedback_notifications'),
]