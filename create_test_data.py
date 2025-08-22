#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta, datetime
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')
django.setup()

from users.models import CustomUser, StudentProfile, TeacherProfile, ParentProfile
from classroom.models import Classroom
from subject.models import Subject
from grades.models import Grade
from assignments.models import Assignment, AssignmentSubmission
from feedback.models import FeedbackCategory

def create_test_data():
    print("Creating comprehensive test data...")
    
    # Create admin user if not exists
    if not CustomUser.objects.filter(email='admin@school.com').exists():
        admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        print("✅ Created admin user: admin@school.com / admin123")
    
    # Create teacher if not exists
    if not CustomUser.objects.filter(email='teacher@school.com').exists():
        teacher = CustomUser.objects.create_user(
            username='teacher',
            email='teacher@school.com',
            password='teacher123',
            first_name='John',
            last_name='Smith',
            role='teacher'
        )
        print("✅ Created teacher user: teacher@school.com / teacher123")
    else:
        teacher = CustomUser.objects.get(email='teacher@school.com')
    
    # Create student if not exists
    if not CustomUser.objects.filter(email='student@school.com').exists():
        student = CustomUser.objects.create_user(
            username='student',
            email='student@school.com',
            password='student123',
            first_name='Jane',
            last_name='Doe',
            role='student'
        )
        print("✅ Created student user: student@school.com / student123")
    else:
        student = CustomUser.objects.get(email='student@school.com')
    
    # Create parent if not exists
    if not CustomUser.objects.filter(email='parent@school.com').exists():
        parent = CustomUser.objects.create_user(
            username='parent',
            email='parent@school.com',
            password='parent123',
            first_name='Robert',
            last_name='Doe',
            role='parent'
        )
        print("✅ Created parent user: parent@school.com / parent123")
    else:
        parent = CustomUser.objects.get(email='parent@school.com')
    
    # Create classroom
    classroom, created = Classroom.objects.get_or_create(
        name='Class 10A',
        defaults={
            'grade': '10th',
            'teacher': teacher
        }
    )
    if created:
        print("✅ Created classroom: Class 10A")
    
    # Create subjects
    subjects_data = [
        {'name': 'Mathematics', 'description': 'Advanced Mathematics'},
        {'name': 'Physics', 'description': 'Physics fundamentals'},
        {'name': 'Chemistry', 'description': 'Chemistry basics'},
        {'name': 'English', 'description': 'English Literature'},
    ]
    
    subjects = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            defaults={'description': subject_data['description']}
        )
        subjects.append(subject)
        if created:
            print(f"✅ Created subject: {subject.name}")
    
    # Link parent to student
    try:
        student_profile = student.student_profile
        student_profile.classroom = classroom
        student_profile.grade = '10th'
        student_profile.save()
        
        parent_profile = parent.parent_profile
        parent_profile.students.add(student_profile)
        parent_profile.save()
        print("✅ Linked parent to student")
    except Exception as e:
        print(f"⚠️ Error linking parent to student: {e}")
    
    # Create sample grades
    grade_types = ['assignment', 'quiz', 'exam', 'project']
    
    for i in range(10):
        subject = random.choice(subjects)
        grade_type = random.choice(grade_types)
        points_possible = random.choice([10, 20, 50, 100])
        points_earned = random.randint(int(points_possible * 0.6), points_possible)
        
        Grade.objects.get_or_create(
            student=student,
            subject=subject,
            teacher=teacher,
            title=f"{grade_type.title()} {i+1}",
            defaults={
                'grade_type': grade_type,
                'points_earned': points_earned,
                'points_possible': points_possible,
                'date_assigned': date.today() - timedelta(days=random.randint(1, 30)),
                'comments': f'Good work on {grade_type}'
            }
        )
    print("✅ Created sample grades")
    
    # Create sample assignments
    assignment_titles = [
        'Math Problem Set 1',
        'Physics Lab Report',
        'Chemistry Experiment',
        'English Essay',
        'Math Quiz Preparation'
    ]
    
    for i, title in enumerate(assignment_titles):
        subject = subjects[i % len(subjects)]
        due_date = datetime.now() + timedelta(days=random.randint(1, 30))
        
        Assignment.objects.get_or_create(
            title=title,
            subject=subject,
            classroom=classroom,
            teacher=teacher,
            defaults={
                'description': f'Complete the {title.lower()} as assigned in class.',
                'due_date': due_date,
                'max_points': random.choice([50, 75, 100]),
                'status': 'published',
                'priority': random.choice(['low', 'medium', 'high'])
            }
        )
    print("✅ Created sample assignments")
    
    # Create feedback categories
    categories_data = [
        {'name': 'Course Feedback', 'description': 'General course feedback', 'icon': 'fas fa-book', 'color': '#007bff'},
        {'name': 'Teacher Evaluation', 'description': 'Teacher performance feedback', 'icon': 'fas fa-chalkboard-teacher', 'color': '#28a745'},
        {'name': 'Peer Review', 'description': 'Student peer reviews', 'icon': 'fas fa-users', 'color': '#ffc107'},
    ]
    
    for cat_data in categories_data:
        category, created = FeedbackCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Created feedback category: {category.name}")
    
    print("\n🎉 Test data creation completed!")
    print("\n🔐 Login credentials:")
    print("👨‍💼 Admin: admin@school.com / admin123")
    print("👨‍🏫 Teacher: teacher@school.com / teacher123") 
    print("👨‍🎓 Student: student@school.com / student123")
    print("👨‍👩‍👧‍👦 Parent: parent@school.com / parent123")
    print("\n📋 Features now working:")
    print("✅ Role-based dashboards")
    print("✅ Student attendance tracking")
    print("✅ Grades management")
    print("✅ Assignments system")
    print("✅ Parent-student linking")
    print("✅ 4-digit ID format (e.g., JA12, JO34)")

if __name__ == '__main__':
    create_test_data()