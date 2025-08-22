from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassroomViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'announcements', AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', include(router.urls)),
]
