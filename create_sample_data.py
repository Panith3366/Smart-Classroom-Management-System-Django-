#!/usr/bin/env python
"""
Create sample data for testing attendance and feedback systems
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')
django.setup()

from django.contrib.auth import get_user_model
from classroom.models import Classroom
from subject.models import Subject
from attendance.models import AttendanceSession, AttendanceRecord
from feedback.models import FeedbackCategory, FeedbackSession, FeedbackResponse

User = get_user_model()

def create_sample_attendance_data():
    """Create sample attendance sessions and records"""
    print("Creating sample attendance data...")
    
    # Get or create a teacher
    teacher, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@example.com',
            'first_name': 'John',
            'last_name': 'Teacher',
            'role': 'teacher',
            'is_staff': True
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print(f"Created teacher: {teacher.username}")
    
    # Get or create students
    students = []
    for i in range(1, 6):
        student, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@example.com',
                'first_name': f'Student',
                'last_name': f'{i}',
                'role': 'student'
            }
        )
        if created:
            student.set_password('student123')
            student.save()
            print(f"Created student: {student.username}")
        students.append(student)
    
    # Get or create classroom
    classroom, created = Classroom.objects.get_or_create(
        name='Class 10A',
        defaults={
            'description': 'Sample classroom for testing',
            'capacity': 30
        }
    )
    if created:
        print(f"Created classroom: {classroom.name}")
    
    # Note: Classroom-student relationship would need to be defined in models
    # For now, we'll skip this assignment
    
    # Get or create subject
    subject, created = Subject.objects.get_or_create(
        name='Mathematics',
        defaults={
            'description': 'Mathematics subject'
        }
    )
    if created:
        print(f"Created subject: {subject.name}")
    
    # Create attendance sessions
    sessions_data = [
        {
            'title': 'Morning Math Class',
            'description': 'Regular mathematics class attendance',
            'status': 'completed',
            'start_time': timezone.now() - timedelta(days=2),
            'end_time': timezone.now() - timedelta(days=2, hours=-1),
        },
        {
            'title': 'Afternoon Math Class',
            'description': 'Afternoon mathematics session',
            'status': 'completed',
            'start_time': timezone.now() - timedelta(days=1),
            'end_time': timezone.now() - timedelta(days=1, hours=-1),
        },
        {
            'title': 'Current Math Class',
            'description': 'Ongoing mathematics class',
            'status': 'active',
            'start_time': timezone.now() - timedelta(minutes=30),
            'end_time': None,
        }
    ]
    
    for session_data in sessions_data:
        session, created = AttendanceSession.objects.get_or_create(
            title=session_data['title'],
            teacher=teacher,
            defaults={
                'description': session_data['description'],
                'classroom': classroom,
                'subject': subject,
                'status': session_data['status'],
                'start_time': session_data['start_time'],
                'end_time': session_data['end_time'],
                'duration_minutes': 60,
                'late_threshold_minutes': 15,
                'attendance_type': 'daily'
            }
        )
        if created:
            print(f"Created attendance session: {session.title}")
            
            # Create attendance records for completed sessions
            if session.status == 'completed':
                statuses = ['present', 'present', 'late', 'present', 'absent']
                for i, student in enumerate(students):
                    record, record_created = AttendanceRecord.objects.get_or_create(
                        session=session,
                        student=student,
                        defaults={
                            'status': statuses[i % len(statuses)],
                            'marked_at': session.start_time + timedelta(minutes=i*5),
                            'marked_by': teacher,
                            'ip_address': '127.0.0.1',
                            'user_agent': 'Sample Browser'
                        }
                    )
                    if record_created:
                        print(f"  - Created attendance record for {student.username}: {record.status}")

def create_sample_feedback_data():
    """Create sample feedback sessions and responses"""
    print("\nCreating sample feedback data...")
    
    # Get teacher and students
    teacher = User.objects.get(username='teacher1')
    students = User.objects.filter(role='student')[:5]
    classroom = Classroom.objects.get(name='Class 10A')
    subject = Subject.objects.get(name='Mathematics')
    
    # Get feedback categories
    categories = FeedbackCategory.objects.all()[:3]
    
    if not categories:
        print("No feedback categories found. Please run populate_data.py first.")
        return
    
    # Create feedback sessions
    sessions_data = [
        {
            'title': 'Mid-term Course Feedback',
            'description': 'Please provide feedback on the mathematics course progress',
            'category': categories[0],
            'status': 'active'
        },
        {
            'title': 'Teacher Performance Review',
            'description': 'Anonymous feedback about teaching effectiveness',
            'category': categories[1] if len(categories) > 1 else categories[0],
            'status': 'active'
        }
    ]
    
    for session_data in sessions_data:
        session, created = FeedbackSession.objects.get_or_create(
            title=session_data['title'],
            created_by=teacher,
            defaults={
                'description': session_data['description'],
                'category': session_data['category'],
                'classroom': classroom,
                'subject': subject,
                'status': session_data['status'],
                'visibility': 'private',
                'allow_anonymous': True,
                'allow_multiple_responses': False,
                'send_notifications': True,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=7)
            }
        )
        if created:
            print(f"Created feedback session: {session.title}")
            
            # Add target users
            session.target_users.set(students)
            
            # Create some sample responses
            sample_responses = [
                {
                    'question_0': '4',  # rating
                    'question_1': 'More practical examples would be helpful',  # text
                    'question_2': 'Practical exercises'  # multiple choice
                },
                {
                    'question_0': '5',
                    'question_1': 'The course is well structured',
                    'question_2': 'Lectures'
                }
            ]
            
            for i, response_data in enumerate(sample_responses):
                if i < len(students):
                    response, response_created = FeedbackResponse.objects.get_or_create(
                        session=session,
                        respondent=students[i],
                        defaults={
                            'response_data': response_data,
                            'is_complete': True,
                            'completion_time_seconds': 180 + i * 30,
                            'submitted_at': timezone.now() - timedelta(hours=i+1)
                        }
                    )
                    if response_created:
                        print(f"  - Created response from {students[i].username}")

def main():
    print("Creating sample data for Attendance and Feedback systems...")
    print("=" * 60)
    
    try:
        create_sample_attendance_data()
        create_sample_feedback_data()
        
        print("\n" + "=" * 60)
        print("✅ Sample data created successfully!")
        print("\nYou can now test:")
        print("1. Attendance system at /attendance/")
        print("2. Feedback system at /feedback/")
        print("\nLogin credentials:")
        print("- Teacher: teacher1 / teacher123")
        print("- Students: student1-student5 / student123")
        print("- Admin: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()