from django.contrib import admin
from .models import (FeedbackCategory, FeedbackTemplate, FeedbackSession, 
                     FeedbackResponse, FeedbackComment, FeedbackAnalytics, 
                     FeedbackNotification)

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(FeedbackTemplate)
class FeedbackTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'template_type', 'category', 'created_by', 'is_public', 'is_active', 'created_at']
    list_filter = ['template_type', 'category', 'is_public', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(FeedbackSession)
class FeedbackSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'classroom', 'subject', 'created_by', 'status', 'visibility', 'response_count', 'completion_rate']
    list_filter = ['status', 'visibility', 'category', 'classroom', 'subject', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'response_count', 'target_count', 'completion_rate', 'is_active']
    filter_horizontal = ['target_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'template', 'category')
        }),
        ('Context', {
            'fields': ('classroom', 'subject', 'created_by', 'target_users')
        }),
        ('Settings', {
            'fields': ('status', 'visibility', 'allow_anonymous', 'allow_multiple_responses')
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date')
        }),
        ('Advanced Features', {
            'fields': ('send_notifications', 'auto_remind', 'reminder_interval_hours'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('response_count', 'target_count', 'completion_rate', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['session', 'respondent', 'is_complete', 'completion_time_seconds', 'submitted_at']
    list_filter = ['is_complete', 'session__category', 'session__classroom', 'submitted_at']
    search_fields = ['session__title', 'respondent__username', 'respondent__first_name', 'respondent__last_name']
    readonly_fields = ['submitted_at', 'updated_at', 'response_data']

@admin.register(FeedbackComment)
class FeedbackCommentAdmin(admin.ModelAdmin):
    list_display = ['response', 'author', 'content_preview', 'parent', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at', 'response__session__category']
    search_fields = ['content', 'author__username', 'response__session__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"

@admin.register(FeedbackAnalytics)
class FeedbackAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['session', 'total_responses', 'response_rate', 'average_completion_time', 'last_calculated']
    list_filter = ['last_calculated', 'session__category', 'session__classroom']
    search_fields = ['session__title']
    readonly_fields = ['last_calculated', 'detailed_metrics']

@admin.register(FeedbackNotification)
class FeedbackNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at']
