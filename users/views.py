from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
import json

from .models import CustomUser, AdminProfile, TeacherProfile, StudentProfile, ParentProfile
from .forms import (CustomUserCreationForm, AdminProfileForm, TeacherProfileForm, 
                   StudentProfileForm, ParentProfileForm, UserProfileForm, StudentCredentialLoginForm)
from .decorators import admin_required, role_required, can_modify_user, user_can_access_student_data
from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)

# API Views (existing)
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return Response({"error": "Registration failed. Please check your data."}, status=status.HTTP_400_BAD_REQUEST)

# Web Views
def signup_view(request):
    """User registration view with role selection"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def student_credential_login(request):
    """Special login for parents using student credentials"""
    if request.method == 'POST':
        form = StudentCredentialLoginForm(request.POST)
        if form.is_valid():
            student_user = form.cleaned_data['student_user']
            # Store student info in session for parent access
            request.session['viewing_student_id'] = student_user.id
            request.session['viewing_student_name'] = student_user.get_full_name()
            messages.success(request, f'Viewing data for student: {student_user.get_full_name()}')
            return redirect('users:student_details_for_parent')
        else:
            messages.error(request, 'Invalid student credentials.')
    else:
        form = StudentCredentialLoginForm()
    
    return render(request, 'registration/student_credential_login.html', {'form': form})

def student_details_for_parent(request, student_id=None):
    """Show student details for parent - can be accessed by logged-in parents or via student credentials"""
    
    # Check if user is logged in as parent
    if request.user.is_authenticated and request.user.role == 'parent':
        # Parent is logged in - show their child's details
        if not student_id:
            messages.error(request, 'Student ID is required.')
            return redirect('users:parent_dashboard')
        
        # Verify this student belongs to this parent
        try:
            parent_profile = request.user.parent_profile
            student = CustomUser.objects.get(id=student_id, role='student')
            
            # Check if this student is linked to this parent
            if not parent_profile.students.filter(user=student).exists():
                messages.error(request, 'You do not have permission to view this student.')
                return redirect('users:parent_dashboard')
                
        except (CustomUser.DoesNotExist, AttributeError):
            messages.error(request, 'Student not found.')
            return redirect('users:parent_dashboard')
    
    else:
        # Not logged in as parent - check session for student credential login
        if not student_id:
            student_id = request.session.get('viewing_student_id')
        
        if not student_id:
            messages.error(request, 'Please login to view student details.')
            return redirect('users:student_credential_login')
        
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Student not found.')
            return redirect('users:student_credential_login')
    
    # Get student profile and data
    try:
        student_profile = getattr(student, 'student_profile', None)
        if not student_profile:
            messages.error(request, 'Student profile not found.')
            return redirect('users:parent_dashboard' if request.user.is_authenticated else 'users:student_credential_login')
        
        # Get student's grades
        try:
            from grades.models import Grade
            grades = Grade.objects.filter(student=student).order_by('-date_assigned')[:10]
        except Exception:
            grades = []
        
        # Get student's attendance records
        try:
            from attendance.models import AttendanceRecord
            attendance_records = AttendanceRecord.objects.filter(student=student).order_by('-session__start_time')[:10]
            
            # Calculate attendance statistics
            total_sessions = AttendanceRecord.objects.filter(student=student).count()
            present_count = AttendanceRecord.objects.filter(student=student, status='present').count()
            attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        except Exception:
            attendance_records = []
            attendance_percentage = 0
        
        # Get assignments
        try:
            from assignments.models import Assignment, AssignmentSubmission
            if student_profile.classroom:
                assignments = Assignment.objects.filter(
                    classroom=student_profile.classroom,
                    status='published'
                ).order_by('-due_date')[:5]
            else:
                assignments = []
            
            submissions = AssignmentSubmission.objects.filter(student=student)
            submission_dict = {sub.assignment.id: sub for sub in submissions}
        except Exception:
            assignments = []
            submission_dict = {}
        
        context = {
            'student': student,
            'student_profile': student_profile,
            'grades': grades,
            'attendance_records': attendance_records,
            'attendance_percentage': round(attendance_percentage, 1),
            'assignments': assignments,
            'submission_dict': submission_dict,
            'is_parent_view': True,
            'is_logged_in_parent': request.user.is_authenticated and request.user.role == 'parent',
        }
        
        return render(request, 'users/student_details_for_parent.html', context)
        
    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('users:parent_dashboard' if request.user.is_authenticated else 'users:student_credential_login')

@login_required
def profile_view(request):
    """View user's own profile"""
    user = request.user
    profile = None
    profile_form = None
    
    # Get the appropriate profile
    if user.role == 'admin':
        profile = getattr(user, 'admin_profile', None)
        profile_form = AdminProfileForm(instance=profile) if profile else None
    elif user.role == 'teacher':
        profile = getattr(user, 'teacher_profile', None)
        profile_form = TeacherProfileForm(instance=profile) if profile else None
    elif user.role == 'student':
        profile = getattr(user, 'student_profile', None)
        profile_form = StudentProfileForm(instance=profile) if profile else None
    elif user.role == 'parent':
        profile = getattr(user, 'parent_profile', None)
        profile_form = ParentProfileForm(instance=profile) if profile else None
    
    user_form = UserProfileForm(instance=user)
    
    context = {
        'user': user,
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user's own profile"""
    user = request.user
    profile = None
    
    # Get the appropriate profile
    if user.role == 'admin':
        profile = getattr(user, 'admin_profile', None)
    elif user.role == 'teacher':
        profile = getattr(user, 'teacher_profile', None)
    elif user.role == 'student':
        profile = getattr(user, 'student_profile', None)
    elif user.role == 'parent':
        profile = getattr(user, 'parent_profile', None)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        # Get the appropriate profile form
        profile_form = None
        if user.role == 'admin' and profile:
            profile_form = AdminProfileForm(request.POST, instance=profile)
        elif user.role == 'teacher' and profile:
            profile_form = TeacherProfileForm(request.POST, instance=profile)
        elif user.role == 'student' and profile:
            profile_form = StudentProfileForm(request.POST, instance=profile)
        elif user.role == 'parent' and profile:
            profile_form = ParentProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = None
        
        if user.role == 'admin' and profile:
            profile_form = AdminProfileForm(instance=profile)
        elif user.role == 'teacher' and profile:
            profile_form = TeacherProfileForm(instance=profile)
        elif user.role == 'student' and profile:
            profile_form = StudentProfileForm(instance=profile)
        elif user.role == 'parent' and profile:
            profile_form = ParentProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'users/edit_profile.html', context)

@admin_required
def user_management(request):
    """Admin view to manage all users"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = CustomUser.objects.all().order_by('-created_at')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': CustomUser.ROLE_CHOICES,
    }
    
    return render(request, 'users/user_management.html', context)

@admin_required
def user_detail(request, user_id):
    """Admin view to see detailed user information"""
    user = get_object_or_404(CustomUser, id=user_id)
    profile = None
    
    if user.role == 'admin':
        profile = getattr(user, 'admin_profile', None)
    elif user.role == 'teacher':
        profile = getattr(user, 'teacher_profile', None)
    elif user.role == 'student':
        profile = getattr(user, 'student_profile', None)
    elif user.role == 'parent':
        profile = getattr(user, 'parent_profile', None)
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'users/user_detail.html', context)

@admin_required
def edit_user(request, user_id):
    """Admin view to edit any user"""
    user = get_object_or_404(CustomUser, id=user_id)
    profile = None
    
    # Get the appropriate profile
    if user.role == 'admin':
        profile = getattr(user, 'admin_profile', None)
    elif user.role == 'teacher':
        profile = getattr(user, 'teacher_profile', None)
    elif user.role == 'student':
        profile = getattr(user, 'student_profile', None)
    elif user.role == 'parent':
        profile = getattr(user, 'parent_profile', None)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        # Get the appropriate profile form
        profile_form = None
        if user.role == 'admin' and profile:
            profile_form = AdminProfileForm(request.POST, instance=profile)
        elif user.role == 'teacher' and profile:
            profile_form = TeacherProfileForm(request.POST, instance=profile)
        elif user.role == 'student' and profile:
            profile_form = StudentProfileForm(request.POST, instance=profile)
        elif user.role == 'parent' and profile:
            profile_form = ParentProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, f'Profile for {user.get_full_name()} updated successfully!')
            return redirect('users:user_detail', user_id=user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = None
        
        if user.role == 'admin' and profile:
            profile_form = AdminProfileForm(instance=profile)
        elif user.role == 'teacher' and profile:
            profile_form = TeacherProfileForm(instance=profile)
        elif user.role == 'student' and profile:
            profile_form = StudentProfileForm(instance=profile)
        elif user.role == 'parent' and profile:
            profile_form = ParentProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'profile': profile,
        'editing_user': True,
    }
    
    return render(request, 'users/edit_profile.html', context)

@admin_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Admin function to activate/deactivate users"""
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active_user = not user.is_active_user
    user.save()
    
    status_text = "activated" if user.is_active_user else "deactivated"
    messages.success(request, f'User {user.get_full_name()} has been {status_text}.')
    
    return redirect('users:user_detail', user_id=user.id)

@login_required
def student_details_for_parent(request, student_id):
    """View for parents to see student details using student credentials"""
    student_user = get_object_or_404(CustomUser, id=student_id, role='student')
    student_profile = getattr(student_user, 'student_profile', None)
    
    # Check if user has permission to view this student
    # Either they're viewing via student credentials or they're a parent of this student
    viewing_student_id = request.session.get('viewing_student_id')
    is_parent_of_student = False
    
    if request.user.role == 'parent' and hasattr(request.user, 'parent_profile'):
        is_parent_of_student = request.user.parent_profile.students.filter(user_id=student_id).exists()
    
    if not (viewing_student_id == student_id or is_parent_of_student or request.user.role in ['admin', 'teacher']):
        messages.error(request, 'You do not have permission to view this student\'s details.')
        return redirect('users:student_credential_login')
    
    # Get attendance data, grades, etc. (you can expand this)
    context = {
        'student': student_user,
        'student_profile': student_profile,
        'viewing_as_parent': True,
    }
    
    return render(request, 'users/student_details_for_parent.html', context)

@role_required(['admin', 'teacher'])
def students_list(request):
    """List all students (for admin and teachers)"""
    search_query = request.GET.get('search', '')
    classroom_filter = request.GET.get('classroom', '')
    grade_filter = request.GET.get('grade', '')
    
    students = StudentProfile.objects.select_related('user', 'classroom').all()
    
    # Filter for teachers - only their students
    if request.user.role == 'teacher':
        teacher_classrooms = request.user.classrooms.all()
        students = students.filter(classroom__in=teacher_classrooms)
    
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
    
    if classroom_filter:
        students = students.filter(classroom_id=classroom_filter)
    
    if grade_filter:
        students = students.filter(grade=grade_filter)
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    from classroom.models import Classroom
    classrooms = Classroom.objects.all()
    if request.user.role == 'teacher':
        classrooms = request.user.classrooms.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'classroom_filter': classroom_filter,
        'grade_filter': grade_filter,
        'classrooms': classrooms,
        'grade_choices': StudentProfile.GRADE_CHOICES,
    }
    
    return render(request, 'users/students_list.html', context)

@role_required(['admin'])
def teachers_list(request):
    """List all teachers (admin only)"""
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    teachers = TeacherProfile.objects.select_related('user').all()
    
    if search_query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(teacher_id__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    if department_filter:
        teachers = teachers.filter(department__icontains=department_filter)
    
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
    }
    
    return render(request, 'users/teachers_list.html', context)

@login_required
def dashboard_redirect(request):
    """Redirect users to appropriate dashboard based on role"""
    if request.user.role == 'admin':
        return redirect('users:admin_dashboard')
    elif request.user.role == 'teacher':
        return redirect('users:teacher_dashboard')
    elif request.user.role == 'student':
        return redirect('users:student_dashboard')
    elif request.user.role == 'parent':
        return redirect('users:parent_dashboard')
    else:
        return redirect('login')

# Dashboard views for different roles
@admin_required
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    total_users = CustomUser.objects.count()
    total_students = CustomUser.objects.filter(role='student').count()
    total_teachers = CustomUser.objects.filter(role='teacher').count()
    total_parents = CustomUser.objects.filter(role='parent').count()
    
    recent_users = CustomUser.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,
        'recent_users': recent_users,
    }
    
    return render(request, 'users/admin_dashboard.html', context)

@role_required(['teacher'])
def teacher_dashboard(request):
    """Teacher dashboard"""
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    classrooms = request.user.classrooms.all()
    
    context = {
        'teacher_profile': teacher_profile,
        'classrooms': classrooms,
    }
    
    return render(request, 'users/teacher_dashboard.html', context)

@role_required(['student'])
def student_dashboard(request):
    """Student dashboard"""
    student_profile = getattr(request.user, 'student_profile', None)
    
    context = {
        'student_profile': student_profile,
    }
    
    return render(request, 'users/student_dashboard.html', context)

@role_required(['parent'])
def parent_dashboard(request):
    """Parent dashboard"""
    parent_profile = getattr(request.user, 'parent_profile', None)
    children = parent_profile.get_children() if parent_profile else []
    
    context = {
        'parent_profile': parent_profile,
        'children': children,
    }
    
    return render(request, 'users/parent_dashboard.html', context)

@admin_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent admin from deactivating themselves
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('users:user_management')
        
        # Toggle the is_active status
        user.is_active = not user.is_active
        user.save()
        
        status_text = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.get_full_name()} has been {status_text}.')
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'User {status_text} successfully',
                'is_active': user.is_active
            })
        else:
            # Regular form submission - redirect back to user management
            return redirect('users:user_management')
        
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        messages.error(request, 'Error updating user status. Please try again.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error updating user status'
            }, status=500)
        else:
            return redirect('users:user_management')
