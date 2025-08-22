from django.contrib import admin
from .models import Classroom, Announcement

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'teacher')
    search_fields = ('name', 'grade', 'teacher__username')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('classroom__name', 'message')
