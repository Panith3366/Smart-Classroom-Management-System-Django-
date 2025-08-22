from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherProfileViewSet, AssignmentViewSet, QuizViewSet

router = DefaultRouter()
router.register(r'teacherprofiles', TeacherProfileViewSet, basename='teacherprofile')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'quizzes', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]
