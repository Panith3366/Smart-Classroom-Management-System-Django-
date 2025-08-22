from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from classroom.models import Classroom
from subject.models import Subject
from django.utils import timezone

User = get_user_model()

class FeedbackCategory(models.Model):
    """Categories for organizing feedback"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-comment')  # Font Awesome icon class
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Feedback Categories"
        ordering = ['name']
        
    def __str__(self):
        return self.name


class FeedbackTemplate(models.Model):
    """Pre-defined feedback templates for quick feedback"""
    TEMPLATE_TYPES = [
        ('teacher_to_student', 'Teacher to Student'),
        ('student_to_teacher', 'Student to Teacher'),
        ('peer_to_peer', 'Peer to Peer'),
        ('self_assessment', 'Self Assessment'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.ForeignKey(FeedbackCategory, on_delete=models.CASCADE)
    
    # Template structure (stored as JSON)
    questions = models.JSONField(default=list)  # List of questions with types (rating, text, multiple_choice)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class FeedbackSession(models.Model):
    """Feedback collection sessions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('anonymous', 'Anonymous'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(FeedbackTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(FeedbackCategory, on_delete=models.CASCADE)
    
    # Context
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    
    # Participants
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_feedback_sessions')
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_feedback_sessions')
    
    # Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    allow_anonymous = models.BooleanField(default=False)
    allow_multiple_responses = models.BooleanField(default=False)
    
    # Timing
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Advanced features
    send_notifications = models.BooleanField(default=True)
    auto_remind = models.BooleanField(default=False)
    reminder_interval_hours = models.PositiveIntegerField(default=24)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        now = timezone.now()
        return (self.status == 'active' and 
                self.start_date <= now and 
                (self.end_date is None or self.end_date >= now))
    
    @property
    def response_count(self):
        return self.feedback_responses.count()
    
    @property
    def target_count(self):
        return self.target_users.count()
    
    @property
    def completion_rate(self):
        if self.target_count == 0:
            return 0
        return round(self.response_count / self.target_count * 100, 2)


class FeedbackResponse(models.Model):
    """Individual feedback responses"""
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, related_name='feedback_responses')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Null for anonymous
    
    # Response data (stored as JSON)
    response_data = models.JSONField(default=dict)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    completion_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    is_complete = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        
    def __str__(self):
        respondent_name = self.respondent.get_full_name() if self.respondent else "Anonymous"
        return f"{respondent_name} - {self.session.title}"


class FeedbackComment(models.Model):
    """Comments and discussions on feedback"""
    response = models.ForeignKey(FeedbackResponse, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    
    # Threading support
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Comment by {self.author.get_full_name()}"


class FeedbackAnalytics(models.Model):
    """Analytics and insights for feedback sessions"""
    session = models.OneToOneField(FeedbackSession, on_delete=models.CASCADE, related_name='analytics')
    
    # Calculated metrics
    total_responses = models.PositiveIntegerField(default=0)
    average_completion_time = models.FloatField(default=0.0)  # in seconds
    response_rate = models.FloatField(default=0.0)  # percentage
    
    # Sentiment analysis (if implemented)
    positive_sentiment_count = models.PositiveIntegerField(default=0)
    negative_sentiment_count = models.PositiveIntegerField(default=0)
    neutral_sentiment_count = models.PositiveIntegerField(default=0)
    
    # Detailed analytics (stored as JSON)
    detailed_metrics = models.JSONField(default=dict)
    
    last_calculated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.session.title}"


class FeedbackNotification(models.Model):
    """Notifications for feedback system"""
    NOTIFICATION_TYPES = [
        ('new_session', 'New Feedback Session'),
        ('reminder', 'Feedback Reminder'),
        ('response_received', 'Response Received'),
        ('session_completed', 'Session Completed'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, null=True, blank=True)
    response = models.ForeignKey(FeedbackResponse, on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"
