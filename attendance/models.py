from django.db import models
from django.contrib.auth import get_user_model
from classroom.models import Classroom
from subject.models import Subject
from django.utils import timezone
from datetime import datetime, time

User = get_user_model()

class AttendanceSession(models.Model):
    """Model for attendance sessions"""
    ATTENDANCE_TYPES = [
        ('daily', 'Daily Attendance'),
        ('subject', 'Subject-wise Attendance'),
        ('event', 'Event Attendance'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES, default='daily')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Time settings
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)  # Default 1 hour
    
    # Advanced features
    auto_close = models.BooleanField(default=True)
    allow_late_marking = models.BooleanField(default=True)
    late_threshold_minutes = models.PositiveIntegerField(default=15)
    
    # Location-based attendance (optional)
    location_required = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_radius_meters = models.PositiveIntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.classroom.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and timezone.now() <= (self.end_time or self.start_time + timezone.timedelta(minutes=self.duration_minutes))
    
    @property
    def total_students(self):
        return self.classroom.students.count()
    
    @property
    def present_count(self):
        return self.attendance_records.filter(status='present').count()
    
    @property
    def absent_count(self):
        return self.attendance_records.filter(status='absent').count()
    
    @property
    def late_count(self):
        return self.attendance_records.filter(status='late').count()
    
    @property
    def attendance_percentage(self):
        if self.total_students == 0:
            return 0
        return round((self.present_count + self.late_count) / self.total_students * 100, 2)


class AttendanceRecord(models.Model):
    """Individual attendance records for students"""
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='absent')
    
    # Timing information
    marked_at = models.DateTimeField(null=True, blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendance')
    
    # Location information (if location-based attendance is enabled)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session', 'student']
        ordering = ['student__first_name', 'student__last_name']
        
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.session.title} - {self.status}"
    
    @property
    def is_late(self):
        if not self.marked_at or not self.session.start_time:
            return False
        late_threshold = self.session.start_time + timezone.timedelta(minutes=self.session.late_threshold_minutes)
        return self.marked_at > late_threshold


class StudentTotalSessions(models.Model):
    """Model to store custom total sessions for students"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_session_totals')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_session_totals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'classroom', 'subject']
        ordering = ['student__first_name', 'student__last_name']
        
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.total_sessions} sessions"


class StudentCustomAttendance(models.Model):
    """Model to store custom attendance counts for students"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    
    # Custom attendance counts
    present_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_custom_attendance')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_custom_attendance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'classroom', 'subject']
        ordering = ['student__first_name', 'student__last_name']
        verbose_name = 'Student Custom Attendance'
        verbose_name_plural = 'Student Custom Attendance Records'
        
    def __str__(self):
        return f"{self.student.get_full_name()} - P:{self.present_count} L:{self.late_count} A:{self.absent_count}"
    
    @property
    def total_custom_sessions(self):
        """Calculate total sessions from custom counts"""
        return self.present_count + self.late_count + self.absent_count


class AttendanceReport(models.Model):
    """Generated attendance reports"""
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('custom', 'Custom Range Report'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'role': 'student'})
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Report data (stored as JSON)
    report_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-generated_at']
        
    def __str__(self):
        return f"{self.title} - {self.report_type}"
