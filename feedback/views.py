from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import (FeedbackCategory, FeedbackTemplate, FeedbackSession, 
                     FeedbackResponse, FeedbackComment, FeedbackAnalytics, 
                     FeedbackNotification)
from classroom.models import Classroom
from subject.models import Subject
from users.models import CustomUser
import json
from datetime import datetime, timedelta

def feedback_list(request):
    """Main feedback page showing feedback forms and submitted responses"""
    # Get feedback sessions where user can respond
    if request.user.is_authenticated:
        available_sessions = FeedbackSession.objects.filter(
            Q(target_users=request.user),
            status='active'
        ).distinct()
        
        # Get user's submitted responses
        submitted_responses = FeedbackResponse.objects.filter(
            respondent=request.user
        ).select_related('session').order_by('-submitted_at')
    else:
        # For anonymous users, show public sessions
        available_sessions = FeedbackSession.objects.filter(
            status='active',
            visibility='public'
        )
        submitted_responses = FeedbackResponse.objects.none()
    
    # Get filter parameters
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    
    # Apply filters to available sessions
    if category_filter:
        available_sessions = available_sessions.filter(category_id=category_filter)
    
    # Apply filters to submitted responses
    if category_filter:
        submitted_responses = submitted_responses.filter(session__category_id=category_filter)
    
    if status_filter == 'completed':
        submitted_responses = submitted_responses.filter(is_complete=True)
    elif status_filter == 'draft':
        submitted_responses = submitted_responses.filter(is_complete=False)
    
    # Pagination for available sessions
    sessions_paginator = Paginator(available_sessions, 10)
    sessions_page = request.GET.get('sessions_page')
    sessions_page_obj = sessions_paginator.get_page(sessions_page)
    
    # Pagination for submitted responses
    responses_paginator = Paginator(submitted_responses, 10)
    responses_page = request.GET.get('responses_page')
    responses_page_obj = responses_paginator.get_page(responses_page)
    
    # Get filter options
    categories = FeedbackCategory.objects.all()
    
    context = {
        'available_sessions': sessions_page_obj,
        'submitted_responses': responses_page_obj,
        'categories': categories,
        'current_filters': {
            'category': category_filter,
            'status': status_filter,
        }
    }
    return render(request, 'feedback/feedback_list.html', context)

@login_required
def feedback_dashboard(request):
    """Main feedback dashboard with overview and quick actions"""
    # Get recent sessions
    recent_sessions = FeedbackSession.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get active sessions
    active_sessions = FeedbackSession.objects.filter(
        status='active',
        created_by=request.user
    )
    
    # Get pending responses (sessions where user is targeted)
    pending_responses = FeedbackSession.objects.filter(
        target_users=request.user,
        status='active'
    ).exclude(
        feedback_responses__respondent=request.user
    )
    
    # Get statistics
    total_sessions = FeedbackSession.objects.filter(created_by=request.user).count()
    total_responses = FeedbackResponse.objects.filter(
        session__created_by=request.user
    ).count()
    
    # Get recent notifications
    notifications = FeedbackNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'recent_sessions': recent_sessions,
        'active_sessions': active_sessions,
        'pending_responses': pending_responses,
        'total_sessions': total_sessions,
        'total_responses': total_responses,
        'notifications': notifications,
    }
    return render(request, 'feedback/dashboard.html', context)

@login_required
def feedback_sessions_list(request):
    """List all feedback sessions with filtering and pagination"""
    sessions = FeedbackSession.objects.filter(created_by=request.user)
    
    # Filtering
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    classroom_filter = request.GET.get('classroom')
    visibility_filter = request.GET.get('visibility')
    
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    if category_filter:
        sessions = sessions.filter(category_id=category_filter)
    if classroom_filter:
        sessions = sessions.filter(classroom_id=classroom_filter)
    if visibility_filter:
        sessions = sessions.filter(visibility=visibility_filter)
    
    # Pagination
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = FeedbackCategory.objects.filter(is_active=True)
    classrooms = Classroom.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'classrooms': classrooms,
        'current_filters': {
            'status': status_filter,
            'category': category_filter,
            'classroom': classroom_filter,
            'visibility': visibility_filter,
        }
    }
    return render(request, 'feedback/sessions_list.html', context)

@login_required
def feedback_session_create(request):
    """Create a new feedback session"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        template_id = request.POST.get('template')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        visibility = request.POST.get('visibility', 'private')
        allow_anonymous = request.POST.get('allow_anonymous') == 'on'
        allow_multiple_responses = request.POST.get('allow_multiple_responses') == 'on'
        end_date = request.POST.get('end_date')
        target_user_ids = request.POST.getlist('target_users')
        
        try:
            category = FeedbackCategory.objects.get(id=category_id)
            template = None
            if template_id:
                template = FeedbackTemplate.objects.get(id=template_id)
            
            classroom = None
            if classroom_id:
                classroom = Classroom.objects.get(id=classroom_id)
            
            subject = None
            if subject_id:
                subject = Subject.objects.get(id=subject_id)
            
            session = FeedbackSession.objects.create(
                title=title,
                description=description,
                category=category,
                template=template,
                classroom=classroom,
                subject=subject,
                created_by=request.user,
                visibility=visibility,
                allow_anonymous=allow_anonymous,
                allow_multiple_responses=allow_multiple_responses,
                end_date=datetime.strptime(end_date, '%Y-%m-%dT%H:%M') if end_date else None,
                status='active'
            )
            
            # Add target users
            if target_user_ids:
                target_users = CustomUser.objects.filter(id__in=target_user_ids)
                session.target_users.set(target_users)
            elif classroom:
                # If no specific users selected but classroom is selected, add all students
                session.target_users.set(classroom.students.all())
            
            messages.success(request, f'Feedback session "{title}" created successfully!')
            return redirect('feedback:feedback_session_detail', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    categories = FeedbackCategory.objects.filter(is_active=True)
    templates = FeedbackTemplate.objects.filter(is_active=True)
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    students = CustomUser.objects.filter(role='student')
    
    context = {
        'categories': categories,
        'templates': templates,
        'classrooms': classrooms,
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'feedback/session_create.html', context)

@login_required
def feedback_session_detail(request, session_id):
    """Detailed view of a feedback session with responses"""
    session = get_object_or_404(FeedbackSession, id=session_id)
    
    # Check permissions
    if session.created_by != request.user and request.user not in session.target_users.all():
        messages.error(request, 'You do not have permission to view this session.')
        return redirect('feedback:feedback_dashboard')
    
    # Get responses
    responses = session.feedback_responses.select_related('respondent').order_by('-submitted_at')
    
    # Check if current user has responded
    user_response = None
    if request.user in session.target_users.all():
        user_response = responses.filter(respondent=request.user).first()
    
    # Get analytics if user is the creator
    analytics = None
    if session.created_by == request.user:
        analytics, created = FeedbackAnalytics.objects.get_or_create(session=session)
        if created or analytics.last_calculated < timezone.now() - timedelta(hours=1):
            # Update analytics
            analytics.total_responses = responses.count()
            analytics.response_rate = session.completion_rate
            if responses.exists():
                completion_times = [r.completion_time_seconds for r in responses if r.completion_time_seconds]
                if completion_times:
                    analytics.average_completion_time = sum(completion_times) / len(completion_times)
            analytics.save()
    
    context = {
        'session': session,
        'responses': responses,
        'user_response': user_response,
        'analytics': analytics,
        'is_creator': session.created_by == request.user,
        'can_respond': request.user in session.target_users.all() and session.is_active,
    }
    return render(request, 'feedback/session_detail.html', context)

@login_required
def feedback_respond(request, session_id):
    """Respond to a feedback session"""
    session = get_object_or_404(FeedbackSession, id=session_id)
    
    # Check if user can respond
    if not session.is_active:
        messages.error(request, 'This feedback session is no longer active.')
        return redirect('feedback:feedback_session_detail', session_id=session.id)
    
    if request.user not in session.target_users.all():
        messages.error(request, 'You are not authorized to respond to this session.')
        return redirect('feedback:feedback_dashboard')
    
    # Check if user has already responded (and multiple responses not allowed)
    existing_response = FeedbackResponse.objects.filter(
        session=session,
        respondent=request.user
    ).first()
    
    if existing_response and not session.allow_multiple_responses:
        messages.info(request, 'You have already responded to this session.')
        return redirect('feedback:feedback_session_detail', session_id=session.id)
    
    if request.method == 'POST':
        try:
            # Get response data from form
            response_data = {}
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    response_data[key] = value
            
            # Calculate completion time (if start time was tracked)
            completion_time = None
            start_time = request.session.get(f'feedback_start_{session_id}')
            if start_time:
                completion_time = int((timezone.now().timestamp() - start_time))
            
            # Create or update response
            if existing_response and session.allow_multiple_responses:
                existing_response.response_data = response_data
                existing_response.completion_time_seconds = completion_time
                existing_response.is_complete = True
                existing_response.save()
                response = existing_response
            else:
                response = FeedbackResponse.objects.create(
                    session=session,
                    respondent=request.user if not session.allow_anonymous else None,
                    response_data=response_data,
                    completion_time_seconds=completion_time,
                    is_complete=True
                )
            
            messages.success(request, 'Your feedback has been submitted successfully!')
            return redirect('feedback:feedback_session_detail', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f'Error submitting feedback: {str(e)}')
    
    # Track start time for completion time calculation
    request.session[f'feedback_start_{session_id}'] = timezone.now().timestamp()
    
    context = {
        'session': session,
        'existing_response': existing_response,
    }
    return render(request, 'feedback/respond.html', context)

@login_required
def feedback_templates(request):
    """Manage feedback templates"""
    templates = FeedbackTemplate.objects.filter(
        Q(created_by=request.user) | Q(is_public=True)
    ).order_by('-created_at')
    
    # Filtering
    template_type = request.GET.get('type')
    category_filter = request.GET.get('category')
    
    if template_type:
        templates = templates.filter(template_type=template_type)
    if category_filter:
        templates = templates.filter(category_id=category_filter)
    
    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = FeedbackCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_filters': {
            'type': template_type,
            'category': category_filter,
        }
    }
    return render(request, 'feedback/templates.html', context)

@login_required
def feedback_analytics(request):
    """Feedback analytics and insights"""
    # Get user's sessions
    sessions = FeedbackSession.objects.filter(created_by=request.user)
    
    # Calculate overall statistics
    total_sessions = sessions.count()
    total_responses = FeedbackResponse.objects.filter(session__created_by=request.user).count()
    active_sessions = sessions.filter(status='active').count()
    
    # Get recent analytics
    recent_analytics = FeedbackAnalytics.objects.filter(
        session__created_by=request.user
    ).order_by('-last_calculated')[:10]
    
    # Get top performing sessions
    top_sessions = sessions.annotate(
        response_count=Count('feedback_responses')
    ).order_by('-response_count')[:5]
    
    context = {
        'total_sessions': total_sessions,
        'total_responses': total_responses,
        'active_sessions': active_sessions,
        'recent_analytics': recent_analytics,
        'top_sessions': top_sessions,
    }
    return render(request, 'feedback/analytics.html', context)

@login_required
def feedback_notifications(request):
    """View and manage feedback notifications"""
    notifications = FeedbackNotification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        notification_id = request.GET.get('mark_read')
        try:
            notification = notifications.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except FeedbackNotification.DoesNotExist:
            return JsonResponse({'success': False})
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'feedback/notifications.html', context)
