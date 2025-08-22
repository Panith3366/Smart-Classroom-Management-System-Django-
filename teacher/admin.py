from django.contrib import admin
from .models import TeacherProfile, Assignment, Quiz

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'subject', 'due_date')
    list_filter = ('due_date',)
    search_fields = ('classroom__name', 'subject__name')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'classroom')
    search_fields = ('title', 'subject__name', 'classroom__name')
