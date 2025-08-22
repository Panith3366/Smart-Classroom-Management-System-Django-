from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import AttendanceSession, AttendanceRecord, AttendanceReport, StudentTotalSessions, StudentCustomAttendance
from classroom.models import Classroom
from subject.models import Subject
from users.models import CustomUser
import json
from datetime import datetime, timedelta

def attendance_list(request):
    """Main attendance page showing student attendance list"""
    # Get all students with their attendance statistics
    students = CustomUser.objects.filter(role='student').select_related('student_profile')
    
    # Get filter parameters
    classroom_filter = request.GET.get('classroom')
    subject_filter = request.GET.get('subject')
    date_filter = request.GET.get('date')
    
    # Apply filters
    if classroom_filter:
        students = students.filter(student_profile__classroom_id=classroom_filter, student_profile__isnull=False)
    
    # Get attendance data for each student
    student_data = []
    for student in students:
        # Ensure student has a profile
        if not hasattr(student, 'student_profile') or not student.student_profile:
            from users.models import StudentProfile
            StudentProfile.objects.get_or_create(user=student)
            student.refresh_from_db()
        
        classroom = student.student_profile.classroom if student.student_profile else None
        
        # Calculate actual attendance statistics from records
        actual_sessions = AttendanceRecord.objects.filter(student=student).count()
        actual_present = AttendanceRecord.objects.filter(student=student, status='present').count()
        actual_late = AttendanceRecord.objects.filter(student=student, status='late').count()
        actual_absent = AttendanceRecord.objects.filter(student=student, status='absent').count()
        
        # Get custom attendance counts if they exist
        try:
            custom_attendance = StudentCustomAttendance.objects.get(
                student=student,
                classroom=classroom
            )
            present_count = custom_attendance.present_count
            late_count = custom_attendance.late_count
            absent_count = custom_attendance.absent_count
            has_custom_attendance = True
        except StudentCustomAttendance.DoesNotExist:
            present_count = actual_present
            late_count = actual_late
            absent_count = actual_absent
            has_custom_attendance = False
        
        # Get custom total sessions or use actual sessions as default
        try:
            custom_sessions = StudentTotalSessions.objects.get(
                student=student,
                classroom=classroom
            )
            total_sessions = custom_sessions.total_sessions
        except StudentTotalSessions.DoesNotExist:
            # Use actual sessions or default
            total_sessions = max(actual_sessions, 30) if actual_sessions > 0 else 30
                
        # If custom attendance exists, recalculate absent count to maintain consistency
        if has_custom_attendance:
            # Recalculate absent count: Total - Present - Late
            absent_count = max(0, total_sessions - present_count - late_count)
        
        # Ensure total_sessions is at least the sum of present + late + absent
        total_sessions = max(total_sessions, present_count + late_count + absent_count)
        
        attendance_percentage = ((present_count + late_count) / total_sessions * 100) if total_sessions > 0 else 0
        
        student_data.append({
            'student': student,
            'total_sessions': total_sessions,
            'actual_sessions': actual_sessions,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'actual_present': actual_present,
            'actual_late': actual_late,
            'actual_absent': actual_absent,
            'has_custom_attendance': has_custom_attendance,
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
                
                # Check if student has a profile and classroom
                if not hasattr(student, 'student_profile') or not student.student_profile:
                    return JsonResponse({
                        'success': False,
                        'message': 'Student profile not found. Please ensure the student is properly registered.'
                    })
                
                if not student.student_profile.classroom:
                    return JsonResponse({
                        'success': False,
                        'message': 'Student is not assigned to any classroom.'
                    })
                
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

@login_required
@require_http_methods(["POST"])
def update_total_sessions(request):
    """AJAX endpoint for updating student total sessions"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        total_sessions = data.get('total_sessions')
        
        if not student_id or total_sessions is None:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        # Validate total_sessions is a positive integer
        try:
            total_sessions = int(total_sessions)
            if total_sessions < 0:
                raise ValueError("Total sessions cannot be negative")
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Total sessions must be a valid positive number'
            })
        
        # Get the student
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        
        # Check if user has permission to edit (admin, teacher)
        if request.user.role not in ['admin', 'teacher']:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied'
            })
        
        # Ensure student has a profile and get classroom
        if not hasattr(student, 'student_profile') or not student.student_profile:
            from users.models import StudentProfile
            StudentProfile.objects.get_or_create(user=student)
            student.refresh_from_db()
        
        classroom = student.student_profile.classroom if student.student_profile else None
        
        # Get actual attendance records count
        actual_sessions = AttendanceRecord.objects.filter(student=student).count()
        
        # Ensure total_sessions is at least as much as actual sessions
        if total_sessions < actual_sessions:
            return JsonResponse({
                'success': False,
                'message': f'Total sessions cannot be less than actual attendance records ({actual_sessions})'
            })
        
        # Create or update StudentTotalSessions record
        session_record, created = StudentTotalSessions.objects.get_or_create(
            student=student,
            classroom=classroom,
            defaults={
                'total_sessions': total_sessions,
                'created_by': request.user,
                'updated_by': request.user,
            }
        )
        
        if not created:
            session_record.total_sessions = total_sessions
            session_record.updated_by = request.user
            session_record.save()
        
        # Recalculate attendance percentage
        present_count = AttendanceRecord.objects.filter(student=student, status='present').count()
        attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        
        return JsonResponse({
            'success': True,
            'message': 'Total sessions updated successfully',
            'total_sessions': total_sessions,
            'attendance_percentage': round(attendance_percentage, 1)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating total sessions: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def update_attendance_count(request):
    """AJAX endpoint for updating student attendance counts (Present, Late, Absent)"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        count_type = data.get('count_type')  # 'present', 'late', or 'absent'
        count_value = data.get('count_value')
        
        if not student_id or not count_type or count_value is None:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        if count_type not in ['present', 'late', 'absent']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid count type. Must be present, late, or absent.'
            })
        
        # Validate count_value is a non-negative integer
        try:
            count_value = int(count_value)
            if count_value < 0:
                raise ValueError("Count cannot be negative")
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Count must be a valid non-negative number'
            })
        
        # Get the student
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        
        # Check if user has permission to edit (admin, teacher)
        if request.user.role not in ['admin', 'teacher']:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied'
            })
        
        # Ensure student has a profile and get classroom
        if not hasattr(student, 'student_profile') or not student.student_profile:
            from users.models import StudentProfile
            StudentProfile.objects.get_or_create(user=student)
            student.refresh_from_db()
        
        classroom = student.student_profile.classroom if student.student_profile else None
        
        # Get or create StudentCustomAttendance record
        from .models import StudentCustomAttendance
        custom_attendance, created = StudentCustomAttendance.objects.get_or_create(
            student=student,
            classroom=classroom,
            defaults={
                'present_count': 0,
                'late_count': 0,
                'absent_count': 0,
                'created_by': request.user,
                'updated_by': request.user,
            }
        )
        
        # If record was just created, initialize with actual attendance counts
        if created:
            actual_present = AttendanceRecord.objects.filter(student=student, status='present').count()
            actual_late = AttendanceRecord.objects.filter(student=student, status='late').count()
            actual_absent = AttendanceRecord.objects.filter(student=student, status='absent').count()
            
            custom_attendance.present_count = actual_present
            custom_attendance.late_count = actual_late
            custom_attendance.absent_count = actual_absent
        
        # Get total sessions for this student
        from .models import StudentTotalSessions
        try:
            total_sessions_obj = StudentTotalSessions.objects.get(
                student=student,
                classroom=classroom
            )
            total_sessions = total_sessions_obj.total_sessions
        except StudentTotalSessions.DoesNotExist:
            # If no custom total sessions, use default or actual count
            total_sessions = AttendanceRecord.objects.filter(student=student).count()
            if total_sessions == 0:
                total_sessions = 30  # Default fallback
        
        # Update the specific count and recalculate related counts
        if count_type == 'present':
            custom_attendance.present_count = count_value
            # Auto-calculate absent: Total - Present - Late
            custom_attendance.absent_count = max(0, total_sessions - count_value - custom_attendance.late_count)
        elif count_type == 'late':
            custom_attendance.late_count = count_value
            # Auto-calculate absent: Total - Present - Late
            custom_attendance.absent_count = max(0, total_sessions - custom_attendance.present_count - count_value)
        elif count_type == 'absent':
            custom_attendance.absent_count = count_value
            # When absent is directly set, don't auto-adjust other counts
        
        custom_attendance.updated_by = request.user
        custom_attendance.save()
        
        # Calculate attendance percentage based on present + late out of total sessions
        attendance_percentage = ((custom_attendance.present_count + custom_attendance.late_count) / total_sessions * 100) if total_sessions > 0 else 0
        
        # Get actual counts for comparison
        actual_present = AttendanceRecord.objects.filter(student=student, status='present').count()
        actual_late = AttendanceRecord.objects.filter(student=student, status='late').count()
        actual_absent = AttendanceRecord.objects.filter(student=student, status='absent').count()
        
        return JsonResponse({
            'success': True,
            'message': f'{count_type.title()} count updated successfully',
            'present_count': custom_attendance.present_count,
            'late_count': custom_attendance.late_count,
            'absent_count': custom_attendance.absent_count,
            'total_sessions': total_sessions,
            'attendance_percentage': round(attendance_percentage, 1),
            'actual_present': actual_present,
            'actual_late': actual_late,
            'actual_absent': actual_absent
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating {count_type} count: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def bulk_update_attendance_counts(request):
    """AJAX endpoint for bulk updating attendance counts"""
    try:
        data = json.loads(request.body)
        count_type = data.get('count_type')  # 'present', 'late', or 'absent'
        count_value = data.get('count_value')
        student_ids = data.get('student_ids', [])
        
        if not count_type or count_value is None:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        if count_type not in ['present', 'late', 'absent']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid count type. Must be present, late, or absent.'
            })
        
        # Validate count_value is a non-negative integer
        try:
            count_value = int(count_value)
            if count_value < 0:
                raise ValueError("Count cannot be negative")
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Count must be a valid non-negative number'
            })
        
        # Check if user has permission to edit (admin, teacher)
        if request.user.role not in ['admin', 'teacher']:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied'
            })
        
        successful_updates = 0
        failed_updates = []
        
        from .models import StudentCustomAttendance
        
        for student_id in student_ids:
            try:
                student = get_object_or_404(CustomUser, id=student_id, role='student')
                
                # Ensure student has a profile and get classroom
                if not hasattr(student, 'student_profile') or not student.student_profile:
                    from users.models import StudentProfile
                    StudentProfile.objects.get_or_create(user=student)
                    student.refresh_from_db()
                
                classroom = student.student_profile.classroom if student.student_profile else None
                
                # Get or create StudentCustomAttendance record
                custom_attendance, created = StudentCustomAttendance.objects.get_or_create(
                    student=student,
                    classroom=classroom,
                    defaults={
                        'present_count': 0,
                        'late_count': 0,
                        'absent_count': 0,
                        'created_by': request.user,
                        'updated_by': request.user,
                    }
                )
                
                # If record was just created, initialize with actual attendance counts
                if created:
                    actual_present = AttendanceRecord.objects.filter(student=student, status='present').count()
                    actual_late = AttendanceRecord.objects.filter(student=student, status='late').count()
                    actual_absent = AttendanceRecord.objects.filter(student=student, status='absent').count()
                    
                    custom_attendance.present_count = actual_present
                    custom_attendance.late_count = actual_late
                    custom_attendance.absent_count = actual_absent
                
                # Get total sessions for this student
                from .models import StudentTotalSessions
                try:
                    total_sessions_obj = StudentTotalSessions.objects.get(
                        student=student,
                        classroom=classroom
                    )
                    total_sessions = total_sessions_obj.total_sessions
                except StudentTotalSessions.DoesNotExist:
                    # If no custom total sessions, use default or actual count
                    total_sessions = AttendanceRecord.objects.filter(student=student).count()
                    if total_sessions == 0:
                        total_sessions = 30  # Default fallback
                
                # Update the specific count and recalculate related counts
                if count_type == 'present':
                    custom_attendance.present_count = count_value
                    # Auto-calculate absent: Total - Present - Late
                    custom_attendance.absent_count = max(0, total_sessions - count_value - custom_attendance.late_count)
                elif count_type == 'late':
                    custom_attendance.late_count = count_value
                    # Auto-calculate absent: Total - Present - Late
                    custom_attendance.absent_count = max(0, total_sessions - custom_attendance.present_count - count_value)
                elif count_type == 'absent':
                    custom_attendance.absent_count = count_value
                    # When absent is directly set, don't auto-adjust other counts
                
                custom_attendance.updated_by = request.user
                custom_attendance.save()
                
                successful_updates += 1
                
            except Exception as e:
                failed_updates.append({
                    'student_id': student_id,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated {count_type} count for {successful_updates} students',
            'successful_updates': successful_updates,
            'failed_updates': len(failed_updates),
            'count_type': count_type,
            'count_value': count_value
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error performing bulk update: {str(e)}'
        }, status=500)