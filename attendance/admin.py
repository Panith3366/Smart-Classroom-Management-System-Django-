from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord, AttendanceReport, StudentTotalSessions, StudentCustomAttendance

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'classroom', 'subject', 'teacher', 'attendance_type', 'status', 'start_time', 'attendance_percentage']
    list_filter = ['attendance_type', 'status', 'classroom', 'subject', 'start_time']
    search_fields = ['title', 'description', 'teacher__username', 'classroom__name']
    readonly_fields = ['created_at', 'updated_at', 'attendance_percentage', 'total_students', 'present_count', 'absent_count', 'late_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'classroom', 'subject', 'teacher', 'attendance_type', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_minutes', 'auto_close', 'allow_late_marking', 'late_threshold_minutes')
        }),
        ('Location Settings', {
            'fields': ('location_required', 'latitude', 'longitude', 'location_radius_meters'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_students', 'present_count', 'absent_count', 'late_count', 'attendance_percentage'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'marked_at', 'marked_by']
    list_filter = ['status', 'session__classroom', 'session__subject', 'marked_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'session__title']
    readonly_fields = ['created_at', 'updated_at', 'is_late']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'student', 'status', 'marked_by', 'marked_at')
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Technical Data', {
            'fields': ('ip_address', 'user_agent', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'is_late'),
            'classes': ('collapse',)
        })
    )

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'classroom', 'subject', 'student', 'start_date', 'end_date', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'classroom', 'subject', 'generated_at']
    search_fields = ['title', 'generated_by__username', 'student__username']
    readonly_fields = ['generated_at', 'report_data']

@admin.register(StudentTotalSessions)
class StudentTotalSessionsAdmin(admin.ModelAdmin):
    list_display = ['student', 'classroom', 'subject', 'total_sessions', 'created_by', 'updated_by', 'updated_at']
    list_filter = ['classroom', 'subject', 'created_at', 'updated_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'classroom', 'subject')
        }),
        ('Session Settings', {
            'fields': ('total_sessions',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(StudentCustomAttendance)
class StudentCustomAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'classroom', 'subject', 'present_count', 'late_count', 'absent_count', 'total_custom_sessions', 'updated_by', 'updated_at']
    list_filter = ['classroom', 'subject', 'created_at', 'updated_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_custom_sessions']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'classroom', 'subject')
        }),
        ('Attendance Counts', {
            'fields': ('present_count', 'late_count', 'absent_count', 'total_custom_sessions')
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Creating new object
            form.base_fields['created_by'].initial = request.user
        form.base_fields['updated_by'].initial = request.user
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
