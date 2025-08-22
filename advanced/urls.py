from django.urls import path
from . import views

app_name = 'advanced'

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('bulk-operations/', views.bulk_operations, name='bulk_operations'),
    path('data-management/', views.data_management, name='data_management'),
    path('automation/', views.smart_automation, name='smart_automation'),
    path('system-config/', views.system_configuration, name='system_configuration'),
    
    # API endpoints
    path('api/export/', views.export_data, name='export_data'),
    path('api/analytics-data/', views.get_analytics_data, name='analytics_data'),
]