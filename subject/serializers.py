from rest_framework import serializers
from .models import Subject, SubjectTeacher

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']

class SubjectTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTeacher
        fields = ['id', 'subject', 'teacher', 'classroom']
