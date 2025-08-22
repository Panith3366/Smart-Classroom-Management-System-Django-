from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Usage: @role_required(['admin', 'teacher'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('users:dashboard_redirect')
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator to restrict access to admin users only."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Admin access required.")
            return redirect('users:dashboard_redirect')
    return _wrapped_view

def teacher_required(view_func):
    """Decorator to restrict access to teacher users only."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['admin', 'teacher']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Teacher access required.")
            return redirect('users:dashboard_redirect')
    return _wrapped_view

def student_required(view_func):
    """Decorator to restrict access to student users only."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['admin', 'student']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Student access required.")
            return redirect('users:dashboard_redirect')
    return _wrapped_view

def parent_required(view_func):
    """Decorator to restrict access to parent users only."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['admin', 'parent']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Parent access required.")
            return redirect('users:dashboard_redirect')
    return _wrapped_view

def teacher_or_admin_required(view_func):
    """Decorator to restrict access to teachers and admins only."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role in ['admin', 'teacher']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Teacher or Admin access required.")
            return redirect('users:dashboard_redirect')
    return _wrapped_view

def can_modify_user(user, target_user):
    """
    Check if a user can modify another user's data.
    Admins can modify anyone.
    Teachers can modify their own data and their students' data.
    Students and parents can only modify their own data.
    """
    if user.role == 'admin':
        return True
    elif user.role == 'teacher':
        if user == target_user:
            return True
        # Teachers can modify their students' data
        if target_user.role == 'student' and hasattr(target_user, 'student_profile'):
            # Check if the student is in any of the teacher's classrooms
            teacher_classrooms = user.classrooms.all()
            student_classroom = target_user.student_profile.classroom
            return student_classroom in teacher_classrooms
    elif user.role == 'parent':
        if user == target_user:
            return True
        # Parents can view their children's data
        if target_user.role == 'student' and hasattr(user, 'parent_profile'):
            return target_user.student_profile in user.parent_profile.students.all()
    elif user.role == 'student':
        return user == target_user
    
    return False

def user_can_access_student_data(user, student_user):
    """
    Check if a user can access student data.
    Used for attendance, grades, etc.
    """
    if user.role == 'admin':
        return True
    elif user.role == 'teacher':
        # Teachers can access their students' data
        if hasattr(student_user, 'student_profile'):
            teacher_classrooms = user.classrooms.all()
            student_classroom = student_user.student_profile.classroom
            return student_classroom in teacher_classrooms
    elif user.role == 'parent':
        # Parents can access their children's data
        if hasattr(user, 'parent_profile') and hasattr(student_user, 'student_profile'):
            return student_user.student_profile in user.parent_profile.students.all()
    elif user.role == 'student':
        # Students can access their own data
        return user == student_user
    
    return False