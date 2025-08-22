from rest_framework import serializers
from .models import Classroom, Announcement

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'grade', 'teacher']

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'classroom', 'message', 'created_at']
        read_only_fields = ['created_at']
