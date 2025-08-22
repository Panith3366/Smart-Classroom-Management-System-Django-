from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Assignment, AssignmentSubmission
from users.models import CustomUser
from classroom.models import Classroom
from subject.models import Subject

@login_required
def assignments_router(request):
    """Route assignments based on user role"""
    if request.user.role == 'student':
        return redirect('assignments:student_assignments')
    elif request.user.role in ['teacher', 'admin']:
        return redirect('assignments:teacher_assignments')
    else:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

@login_required
def student_assignments(request):
    """View assignments for students"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get student's classroom assignments
    student_profile = request.user.student_profile
    if not student_profile.classroom:
        assignments = []
    else:
        assignments = Assignment.objects.filter(
            classroom=student_profile.classroom,
            status='published'
        ).order_by('-due_date')
    
    # Get submissions for this student
    submissions = AssignmentSubmission.objects.filter(student=request.user)
    submission_dict = {sub.assignment.id: sub for sub in submissions}
    
    # Combine assignments with submission status
    assignment_data = []
    for assignment in assignments:
        submission = submission_dict.get(assignment.id)
        assignment_data.append({
            'assignment': assignment,
            'submission': submission,
            'status': submission.status if submission else 'not_submitted',
            'is_overdue': assignment.due_date < timezone.now() and not submission,
        })
    
    context = {
        'assignment_data': assignment_data,
        'student': request.user,
    }
    return render(request, 'assignments/student_list.html', context)

@login_required
def assignment_detail(request, assignment_id):
    """View assignment details"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if student can view this assignment
    if request.user.role == 'student':
        # Check if student has profile and classroom
        if not hasattr(request.user, 'student_profile') or not request.user.student_profile:
            messages.error(request, 'Student profile not found. Please contact administrator.')
            return redirect('assignments:student_assignments')
            
        if not request.user.student_profile.classroom or request.user.student_profile.classroom != assignment.classroom:
            messages.error(request, 'You cannot view this assignment.')
            return redirect('assignments:student_assignments')
        
        # Get student's submission if exists
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user)
        except AssignmentSubmission.DoesNotExist:
            submission = None
    else:
        submission = None
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'can_submit': request.user.role == 'student' and assignment.status == 'published',
        'is_overdue': assignment.due_date < timezone.now(),
    }
    return render(request, 'assignments/detail.html', context)

@login_required
def submit_assignment(request, assignment_id):
    """Submit an assignment"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if student has profile and can submit
    if not hasattr(request.user, 'student_profile') or not request.user.student_profile:
        messages.error(request, 'Student profile not found. Please contact administrator.')
        return redirect('assignments:student_assignments')
        
    if request.user.student_profile.classroom != assignment.classroom:
        messages.error(request, 'You cannot submit to this assignment.')
        return redirect('assignments:student_assignments')
    
    if request.method == 'POST':
        submission_text = request.POST.get('submission_text', '')
        submission_file = request.FILES.get('submission_file')
        
        # Create or update submission
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=request.user,
            defaults={
                'submission_text': submission_text,
                'submission_file': submission_file,
            }
        )
        
        if not created:
            # Update existing submission
            submission.submission_text = submission_text
            if submission_file:
                submission.submission_file = submission_file
            submission.submitted_at = timezone.now()
            submission.save()
        
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('assignments:assignment_detail', assignment_id=assignment.id)
    
    context = {
        'assignment': assignment,
    }
    return render(request, 'assignments/submit.html', context)

@login_required
def teacher_assignments(request):
    """View assignments for teachers"""
    if request.user.role not in ['teacher', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get assignments created by this teacher or all if admin
    if request.user.role == 'teacher':
        assignments = Assignment.objects.filter(teacher=request.user)
    else:
        assignments = Assignment.objects.all()
    
    assignments = assignments.select_related('classroom', 'subject').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'assignments': assignments,
    }
    return render(request, 'assignments/teacher_list.html', context)

@login_required
def create_assignment(request):
    """Create new assignment"""
    if request.user.role not in ['teacher', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        max_points = request.POST.get('max_points', 100)
        
        try:
            classroom = Classroom.objects.get(id=classroom_id)
            subject = Subject.objects.get(id=subject_id) if subject_id else None
            
            assignment = Assignment.objects.create(
                title=title,
                description=description,
                classroom=classroom,
                subject=subject,
                teacher=request.user,
                due_date=due_date,
                max_points=max_points,
                status='published'
            )
            
            messages.success(request, f'Assignment "{title}" created successfully!')
            return redirect('assignments:teacher_assignments')
            
        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')
    
    # Get context for form
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'classrooms': classrooms,
        'subjects': subjects,
    }
    return render(request, 'assignments/create.html', context)

@login_required
def assignment_submissions(request, assignment_id):
    """View submissions for an assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check permissions
    if request.user.role == 'teacher' and assignment.teacher != request.user:
        messages.error(request, 'You can only view submissions for your own assignments.')
        return redirect('assignments:teacher_assignments')
    
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'assignments/submissions.html', context)