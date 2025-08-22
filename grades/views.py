from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Grade
from users.models import CustomUser

@login_required
def student_grades(request, student_id=None):
    """View student grades"""
    if student_id:
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        # Check permissions
        if request.user.role == 'student' and request.user.id != int(student_id):
            messages.error(request, 'You can only view your own grades.')
            return redirect('grades:my_grades')
    else:
        if request.user.role == 'student':
            student = request.user
        else:
            messages.error(request, 'Student ID required.')
            return redirect('dashboard')
    
    # Get grades for the student
    grades = Grade.objects.filter(student=student).select_related('subject', 'teacher')
    
    # Calculate statistics
    total_grades = grades.count()
    average_grade = grades.aggregate(avg=Avg('percentage'))['avg'] or 0
    
    # Group by subject
    subjects_stats = {}
    for grade in grades:
        subject_name = grade.subject.name
        if subject_name not in subjects_stats:
            subjects_stats[subject_name] = {
                'grades': [],
                'average': 0,
                'count': 0
            }
        subjects_stats[subject_name]['grades'].append(grade)
    
    # Calculate subject averages
    for subject, stats in subjects_stats.items():
        if stats['grades']:
            stats['average'] = sum(g.percentage for g in stats['grades']) / len(stats['grades'])
            stats['count'] = len(stats['grades'])
    
    context = {
        'student': student,
        'grades': grades[:20],  # Recent 20 grades
        'total_grades': total_grades,
        'average_grade': round(average_grade, 2),
        'subjects_stats': subjects_stats,
    }
    
    return render(request, 'grades/student_grades.html', context)