from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, SubjectTeacherViewSet, subject_list, subject_page, subject_add, subject_edit, subject_delete


router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'subjectteachers', SubjectTeacherViewSet, basename='subjectteacher')

urlpatterns = [
    path('', include(router.urls)),
    path('list/', subject_list, name='subject_list'),
    path('add/', subject_add, name='add_subject'),
    path('edit/<int:pk>/', subject_edit, name='edit_subject'),
    path('delete/<int:pk>/', subject_delete, name='delete_subject'),
    path('page/', subject_page, name='subject_page'),
]

