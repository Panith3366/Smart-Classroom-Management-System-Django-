from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import AttendanceSession, AttendanceRecord, AttendanceReport
from classroom.models import Classroom
from subject.models import Subject
from users.models import CustomUser
import json
from datetime import datetime, timedelta

def attendance_list(request):
    """Main attendance page showing student attendance list"""
    # Get all students with their attendance statistics
    students = CustomUser.objects.filter(role='student')
    
    # Get filter parameters
    classroom_filter = request.GET.get('classroom')
    subject_filter = request.GET.get('subject')
    date_filter = request.GET.get('date')
    
    # Apply filters
    if classroom_filter:
        students = students.filter(student_profile__classroom_id=classroom_filter)
    
    # Get attendance data for each student
    student_data = []
    for student in students:
        # Calculate attendance statistics
        total_sessions = AttendanceRecord.objects.filter(student=student).count()
        present_count = AttendanceRecord.objects.filter(student=student, status='present').count()
        late_count = AttendanceRecord.objects.filter(student=student, status='late').count()
        absent_count = AttendanceRecord.objects.filter(student=student, status='absent').count()
        
        attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        
        student_data.append({
            'student': student,
            'total_sessions': total_sessions,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'attendance_percentage': round(attendance_percentage, 1)
        })
    
    # Pagination
    paginator = Paginator(student_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'page_obj': page_obj,
        'classrooms': classrooms,
        'subjects': subjects,
        'current_filters': {
            'classroom': classroom_filter,
            'subject': subject_filter,
            'date': date_filter,
        }
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
def attendance_dashboard(request):
    """Main attendance dashboard with overview and quick actions"""
    # Get recent sessions
    recent_sessions = AttendanceSession.objects.filter(
        teacher=request.user
    ).order_by('-created_at')[:5]
    
    # Get active sessions
    active_sessions = AttendanceSession.objects.filter(
        status='active',
        teacher=request.user
    )
    
    # Get statistics
    total_sessions = AttendanceSession.objects.filter(teacher=request.user).count()
    today_sessions = AttendanceSession.objects.filter(
        teacher=request.user,
        start_time__date=timezone.now().date()
    ).count()
    
    context = {
        'recent_sessions': recent_sessions,
        'active_sessions': active_sessions,
        'total_sessions': total_sessions,
        'today_sessions': today_sessions,
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def attendance_sessions_list(request):
    """List all attendance sessions with filtering and pagination"""
    sessions = AttendanceSession.objects.filter(teacher=request.user)
    
    # Filtering
    status_filter = request.GET.get('status')
    classroom_filter = request.GET.get('classroom')
    subject_filter = request.GET.get('subject')
    date_filter = request.GET.get('date')
    
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    if classroom_filter:
        sessions = sessions.filter(classroom_id=classroom_filter)
    if subject_filter:
        sessions = sessions.filter(subject_id=subject_filter)
    if date_filter:
        sessions = sessions.filter(start_time__date=date_filter)
    
    # Pagination
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'page_obj': page_obj,
        'classrooms': classrooms,
        'subjects': subjects,
        'current_filters': {
            'status': status_filter,
            'classroom': classroom_filter,
            'subject': subject_filter,
            'date': date_filter,
        }
    }
    return render(request, 'attendance/sessions_list.html', context)

@login_required
def attendance_session_create(request):
    """Create a new attendance session"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        attendance_type = request.POST.get('attendance_type', 'daily')
        duration_minutes = int(request.POST.get('duration_minutes', 60))
        
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            subject = Subject.objects.get(id=subject_id) if subject_id else None
            
            session = AttendanceSession.objects.create(
                title=title,
                description=description,
                classroom=classroom,
                subject=subject,
                teacher=request.user,
                attendance_type=attendance_type,
                duration_minutes=duration_minutes,
                end_time=timezone.now() + timedelta(minutes=duration_minutes)
            )
            
            messages.success(request, f'Attendance session "{title}" created successfully!')
            return redirect('attendance:attendance_session_detail', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    # Get context for form
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'classrooms': classrooms,
        'subjects': subjects,
    }
    return render(request, 'attendance/session_create.html', context)

@login_required
def attendance_session_detail(request, session_id):
    """View and manage a specific attendance session"""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Get all students in the classroom
    students = CustomUser.objects.filter(
        role='student',
        student_profile__classroom=session.classroom
    )
    
    # Get existing attendance records
    records = AttendanceRecord.objects.filter(session=session)
    records_dict = {record.student.id: record for record in records}
    
    # Combine students with their attendance status
    student_attendance = []
    for student in students:
        record = records_dict.get(student.id)
        student_attendance.append({
            'student': student,
            'record': record,
            'status': record.status if record else 'not_marked'
        })
    
    context = {
        'session': session,
        'student_attendance': student_attendance,
        'can_edit': session.teacher == request.user,
    }
    return render(request, 'attendance/session_detail.html', context)

@login_required
def attendance_mark_ajax(request):
    """AJAX endpoint for marking individual attendance"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            record_id = data.get('record_id')
            status = data.get('status')
            quick_mark = data.get('quick_mark', False)
            
            if quick_mark and student_id:
                # Quick marking - create or find today's session
                student = CustomUser.objects.get(id=student_id, role='student')
                today = timezone.now().date()
                
                # Try to find an active session for today
                session = AttendanceSession.objects.filter(
                    classroom=student.student_profile.classroom,
                    start_time__date=today,
                    status='active'
                ).first()
                
                if not session:
                    # Create a quick session for today
                    session = AttendanceSession.objects.create(
                        title=f"Quick Attendance - {today}",
                        classroom=student.student_profile.classroom,
                        teacher=request.user,
                        attendance_type='daily',
                        start_time=timezone.now(),
                        end_time=timezone.now() + timedelta(hours=1)
                    )
                
                # Create or update attendance record
                record, created = AttendanceRecord.objects.get_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status}
                )
                
                if not created:
                    record.status = status
                
                record.marked_at = timezone.now()
                record.marked_by = request.user
                record.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Attendance marked as {status}',
                    'record_id': record.id
                })
            
            elif record_id:
                # Update existing record
                record = AttendanceRecord.objects.get(id=record_id)
                record.status = status
                record.marked_at = timezone.now()
                record.marked_by = request.user
                record.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Attendance updated to {status}',
                    'record_id': record.id
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid request parameters'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def attendance_student_profile(request, student_id):
    """View individual student attendance profile"""
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    
    # Check permissions
    if request.user.role == 'student' and request.user.id != int(student_id):
        messages.error(request, 'You can only view your own attendance.')
        return redirect('attendance:attendance_student_profile', student_id=request.user.id)
    
    # Get attendance records
    records = AttendanceRecord.objects.filter(student=student).order_by('-session__start_time')
    
    # Calculate statistics
    total_sessions = records.count()
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = records.filter(status='absent').count()
    
    attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
    
    # Get recent records for display
    recent_records = records[:20]
    
    context = {
        'student': student,
        'records': recent_records,
        'total_sessions': total_sessions,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'attendance_percentage': round(attendance_percentage, 1),
    }
    return render(request, 'attendance/student_profile.html', context)

@login_required
def attendance_reports(request):
    """Generate attendance reports"""
    # Get filter parameters
    classroom_filter = request.GET.get('classroom')
    subject_filter = request.GET.get('subject')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    sessions = AttendanceSession.objects.all()
    
    if classroom_filter:
        sessions = sessions.filter(classroom_id=classroom_filter)
    if subject_filter:
        sessions = sessions.filter(subject_id=subject_filter)
    if date_from:
        sessions = sessions.filter(start_time__date__gte=date_from)
    if date_to:
        sessions = sessions.filter(start_time__date__lte=date_to)
    
    # Get filter options
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'sessions': sessions,
        'classrooms': classrooms,
        'subjects': subjects,
        'current_filters': {
            'classroom': classroom_filter,
            'subject': subject_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'attendance/reports.html', context)