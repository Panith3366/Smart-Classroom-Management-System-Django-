from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from users.models import CustomUser
from teacher.models import TeacherProfile, Assignment, Quiz
from subject.models import Subject, SubjectTeacher
from classroom.models import Classroom, Announcement


def home(request):
    """Dashboard view with overview statistics"""
    # If user is logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('users:admin_dashboard')
        elif request.user.role == 'teacher':
            return redirect('users:teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('users:student_dashboard')
        elif request.user.role == 'parent':
            return redirect('users:parent_dashboard')
    
    # For anonymous users, show general dashboard
    context = {
        'total_teachers': CustomUser.objects.filter(role='teacher').count(),
        'total_students': CustomUser.objects.filter(role='student').count(),
        'total_subjects': Subject.objects.count(),
        'total_classrooms': Classroom.objects.count(),
        'total_assignments': Assignment.objects.count(),
        'total_quizzes': Quiz.objects.count(),
        'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)


def teachers_list(request):
    """Display all teachers with their profiles"""
    teachers = CustomUser.objects.filter(role='teacher').select_related('teacher_profile')
    return render(request, 'teachers/teachers_list.html', {'teachers': teachers})


def teacher_add(request):
    """Add new teacher"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        
        # Set default password if none provided
        if not password:
            password = 'teacher123'
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'teachers/teacher_add.html')
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role='teacher'
        )
        
        TeacherProfile.objects.create(user=user)
        messages.success(request, 'Teacher added successfully!')
        return redirect('teachers_list')
    
    return render(request, 'teachers/teacher_add.html')


def teacher_edit(request, teacher_id):
    """Edit teacher details"""
    teacher = get_object_or_404(CustomUser, id=teacher_id, role='teacher')
    
    if request.method == 'POST':
        teacher.username = request.POST.get('username')
        teacher.email = request.POST.get('email')
        teacher.first_name = request.POST.get('first_name')
        teacher.last_name = request.POST.get('last_name')
        teacher.save()
        
        messages.success(request, 'Teacher updated successfully!')
        return redirect('teachers_list')
    
    return render(request, 'teachers/teacher_edit.html', {'teacher': teacher})


def teacher_delete(request, teacher_id):
    """Delete teacher"""
    teacher = get_object_or_404(CustomUser, id=teacher_id, role='teacher')
    teacher.delete()
    messages.success(request, 'Teacher deleted successfully!')
    return redirect('teachers_list')


def assignments_list(request):
    """Display all assignments"""
    assignments = Assignment.objects.all().select_related('classroom', 'subject')
    return render(request, 'assignments/assignments_list.html', {'assignments': assignments})


def assignment_add(request):
    """Add new assignment"""
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        file = request.FILES.get('file')
        due_date = request.POST.get('due_date')
        
        Assignment.objects.create(
            classroom_id=classroom_id,
            subject_id=subject_id,
            file=file,
            due_date=due_date
        )
        
        messages.success(request, 'Assignment added successfully!')
        return redirect('assignments_list')
    
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'assignments/assignment_add.html', {
        'classrooms': classrooms,
        'subjects': subjects
    })


def assignment_edit(request, assignment_id):
    """Edit assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        assignment.classroom_id = request.POST.get('classroom')
        assignment.subject_id = request.POST.get('subject')
        if request.FILES.get('file'):
            assignment.file = request.FILES.get('file')
        assignment.due_date = request.POST.get('due_date')
        assignment.save()
        
        messages.success(request, 'Assignment updated successfully!')
        return redirect('assignments_list')
    
    classrooms = Classroom.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'assignments/assignment_edit.html', {
        'assignment': assignment,
        'classrooms': classrooms,
        'subjects': subjects
    })


def assignment_delete(request, assignment_id):
    """Delete assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully!')
    return redirect('assignments_list')


def quizzes_list(request):
    """Display all quizzes"""
    quizzes = Quiz.objects.all().select_related('subject', 'classroom')
    return render(request, 'quizzes/quizzes_list.html', {'quizzes': quizzes})


def quiz_add(request):
    """Add new quiz"""
    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        classroom_id = request.POST.get('classroom')
        questions_json = request.POST.get('questions', '[]')
        
        try:
            questions = json.loads(questions_json)
        except json.JSONDecodeError:
            questions = []
        
        Quiz.objects.create(
            title=title,
            subject_id=subject_id,
            classroom_id=classroom_id,
            questions=questions
        )
        
        messages.success(request, 'Quiz added successfully!')
        return redirect('quizzes_list')
    
    subjects = Subject.objects.all()
    classrooms = Classroom.objects.all()
    return render(request, 'quizzes/quiz_add.html', {
        'subjects': subjects,
        'classrooms': classrooms
    })


def quiz_edit(request, quiz_id):
    """Edit quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title')
        quiz.subject_id = request.POST.get('subject')
        quiz.classroom_id = request.POST.get('classroom')
        questions_json = request.POST.get('questions', '[]')
        
        try:
            quiz.questions = json.loads(questions_json)
        except json.JSONDecodeError:
            quiz.questions = []
        
        quiz.save()
        messages.success(request, 'Quiz updated successfully!')
        return redirect('quizzes_list')
    
    subjects = Subject.objects.all()
    classrooms = Classroom.objects.all()
    return render(request, 'quizzes/quiz_edit.html', {
        'quiz': quiz,
        'subjects': subjects,
        'classrooms': classrooms,
        'questions_json': json.dumps(quiz.questions)
    })


def quiz_delete(request, quiz_id):
    """Delete quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully!')
    return redirect('quizzes_list')


def subjects_list(request):
    """Display all subjects"""
    subjects = Subject.objects.all()
    return render(request, 'subjects/subjects_list.html', {'subjects': subjects})


def subject_add(request):
    """Add new subject"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        Subject.objects.create(name=name, description=description)
        messages.success(request, 'Subject added successfully!')
        return redirect('subjects_list')
    
    return render(request, 'subjects/subject_add.html')


def subject_edit(request, subject_id):
    """Edit subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.description = request.POST.get('description', '')
        subject.save()
        
        messages.success(request, 'Subject updated successfully!')
        return redirect('subjects_list')
    
    return render(request, 'subjects/subject_edit.html', {'subject': subject})


def subject_delete(request, subject_id):
    """Delete subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted successfully!')
    return redirect('subjects_list')


def subject_teachers_list(request):
    """Display all subject-teacher assignments"""
    subject_teachers = SubjectTeacher.objects.all().select_related('subject', 'teacher', 'classroom')
    return render(request, 'subject_teachers/subject_teachers_list.html', {'subject_teachers': subject_teachers})


def subject_teacher_add(request):
    """Add new subject-teacher assignment"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        classroom_id = request.POST.get('classroom')
        
        SubjectTeacher.objects.create(
            subject_id=subject_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id
        )
        
        messages.success(request, 'Subject-Teacher assignment added successfully!')
        return redirect('subject_teachers_list')
    
    subjects = Subject.objects.all()
    teachers = CustomUser.objects.filter(role='teacher')
    classrooms = Classroom.objects.all()
    return render(request, 'subject_teachers/subject_teacher_add.html', {
        'subjects': subjects,
        'teachers': teachers,
        'classrooms': classrooms
    })


def subject_teacher_edit(request, st_id):
    """Edit subject-teacher assignment"""
    subject_teacher = get_object_or_404(SubjectTeacher, id=st_id)
    
    if request.method == 'POST':
        subject_teacher.subject_id = request.POST.get('subject')
        subject_teacher.teacher_id = request.POST.get('teacher')
        subject_teacher.classroom_id = request.POST.get('classroom')
        subject_teacher.save()
        
        messages.success(request, 'Subject-Teacher assignment updated successfully!')
        return redirect('subject_teachers_list')
    
    subjects = Subject.objects.all()
    teachers = CustomUser.objects.filter(role='teacher')
    classrooms = Classroom.objects.all()
    return render(request, 'subject_teachers/subject_teacher_edit.html', {
        'subject_teacher': subject_teacher,
        'subjects': subjects,
        'teachers': teachers,
        'classrooms': classrooms
    })


def subject_teacher_delete(request, st_id):
    """Delete subject-teacher assignment"""
    subject_teacher = get_object_or_404(SubjectTeacher, id=st_id)
    subject_teacher.delete()
    messages.success(request, 'Subject-Teacher assignment deleted successfully!')
    return redirect('subject_teachers_list')


# Students Management Views
def students_list(request):
    """Display all students"""
    students = CustomUser.objects.filter(role='student')
    return render(request, 'students/students_list.html', {'students': students})


def student_add(request):
    """Add new student"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        
        # Set default password if none provided
        if not password:
            password = 'student123'
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'students/student_add.html')
        
        CustomUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role='student'
        )
        
        messages.success(request, 'Student added successfully!')
        return redirect('students_list')
    
    return render(request, 'students/student_add.html')


def student_edit(request, student_id):
    """Edit student details"""
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    
    if request.method == 'POST':
        student.username = request.POST.get('username')
        student.email = request.POST.get('email')
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('students_list')
    
    return render(request, 'students/student_edit.html', {'student': student})


def student_delete(request, student_id):
    """Delete student"""
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    student.delete()
    messages.success(request, 'Student deleted successfully!')
    return redirect('students_list')


# Classrooms Management Views
def classrooms_list(request):
    """Display all classrooms"""
    classrooms = Classroom.objects.all().select_related('teacher')
    return render(request, 'classrooms/classrooms_list.html', {'classrooms': classrooms})


def classroom_add(request):
    """Add new classroom"""
    if request.method == 'POST':
        name = request.POST.get('name')
        grade = request.POST.get('grade')
        teacher_id = request.POST.get('teacher')
        
        Classroom.objects.create(
            name=name,
            grade=grade,
            teacher_id=teacher_id
        )
        
        messages.success(request, 'Classroom added successfully!')
        return redirect('classrooms_list')
    
    teachers = CustomUser.objects.filter(role='teacher')
    return render(request, 'classrooms/classroom_add.html', {'teachers': teachers})


def classroom_edit(request, classroom_id):
    """Edit classroom details"""
    classroom = get_object_or_404(Classroom, id=classroom_id)
    
    if request.method == 'POST':
        classroom.name = request.POST.get('name')
        classroom.grade = request.POST.get('grade')
        classroom.teacher_id = request.POST.get('teacher')
        classroom.save()
        
        messages.success(request, 'Classroom updated successfully!')
        return redirect('classrooms_list')
    
    teachers = CustomUser.objects.filter(role='teacher')
    return render(request, 'classrooms/classroom_edit.html', {
        'classroom': classroom,
        'teachers': teachers
    })


def classroom_delete(request, classroom_id):
    """Delete classroom"""
    classroom = get_object_or_404(Classroom, id=classroom_id)
    classroom.delete()
    messages.success(request, 'Classroom deleted successfully!')
    return redirect('classrooms_list')


def custom_logout(request):
    """Custom logout view that redirects to login with success message"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('/login/?logout=1')

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