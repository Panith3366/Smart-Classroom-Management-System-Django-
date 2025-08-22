from django.contrib import admin
from .models import Subject, SubjectTeacher

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'classroom')
    search_fields = ('subject__name', 'teacher__username', 'classroom__name')
