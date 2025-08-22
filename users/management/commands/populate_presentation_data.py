from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random

from users.models import CustomUser, StudentProfile, TeacherProfile, AdminProfile, ParentProfile
from classroom.models import Classroom
from subject.models import Subject
from attendance.models import AttendanceSession, AttendanceRecord, StudentTotalSessions
from grades.models import Grade
from assignments.models import Assignment, AssignmentSubmission


class Command(BaseCommand):
    help = 'Populate database with presentation-ready sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating presentation data...'))
        
        with transaction.atomic():
            self.create_basic_data()
            self.create_comprehensive_users()
            self.create_attendance_data()
            self.create_grades_and_assignments()
            
        self.stdout.write(self.style.SUCCESS('✅ Presentation data created successfully!'))
        self.print_summary()

    def create_basic_data(self):
        """Create classrooms and subjects"""
        # Create default teacher first
        default_teacher, _ = CustomUser.objects.get_or_create(
            username='default_teacher',
            defaults={
                'email': 'default@smartschool.edu',
                'first_name': 'Default',
                'last_name': 'Teacher',
                'role': 'teacher',
                'is_active': True
            }
        )
        if _:
            default_teacher.set_password('teacher123')
            default_teacher.save()
        
        # Create classrooms
        classrooms_data = [
            {'name': 'Grade 10-A', 'grade': '10th'},
            {'name': 'Grade 10-B', 'grade': '10th'},
            {'name': 'Grade 11-A', 'grade': '11th'},
            {'name': 'Grade 11-B', 'grade': '11th'},
            {'name': 'Grade 12-A', 'grade': '12th'},
        ]
        
        for data in classrooms_data:
            Classroom.objects.get_or_create(
                name=data['name'],
                defaults={
                    'name': data['name'],
                    'grade': data['grade'],
                    'teacher': default_teacher
                }
            )
        
        # Create subjects
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English Literature', 'History', 'Computer Science', 'Economics']
        for subject_name in subjects:
            Subject.objects.get_or_create(
                name=subject_name,
                defaults={'description': f'Comprehensive {subject_name} curriculum'}
            )
        
        self.stdout.write('Created classrooms and subjects')

    def create_comprehensive_users(self):
        """Create users with detailed profiles"""
        
        # Create admin users
        admin_users = [
            ('admin_principal', 'Dr. Robert', 'Anderson', 'principal@smartschool.edu', '+1-555-0101'),
            ('admin_vice', 'Ms. Sarah', 'Thompson', 'vice.principal@smartschool.edu', '+1-555-0102'),
        ]
        
        for username, first_name, last_name, email, phone in admin_users:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': phone,
                    'address': f'{random.randint(100, 999)} Education Ave, Academic City, AC {random.randint(10000, 99999)}',
                    'date_of_birth': f'19{random.randint(70, 85)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'role': 'admin',
                    'is_staff': True,
                    'is_active': True
                }
            )
            if created:
                user.set_password('admin123')
                user.save()
                AdminProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'department': 'Administration',
                        'employee_id': f"ADM{random.randint(1000, 9999)}",
                    }
                )
        
        # Create teacher users
        teacher_data = [
            ('teacher_math', 'Dr. Michael', 'Johnson', 'math.teacher@smartschool.edu', 'Mathematics'),
            ('teacher_physics', 'Dr. Emily', 'Davis', 'physics.teacher@smartschool.edu', 'Physics'),
            ('teacher_chemistry', 'Prof. David', 'Wilson', 'chemistry.teacher@smartschool.edu', 'Chemistry'),
            ('teacher_english', 'Ms. Jennifer', 'Brown', 'english.teacher@smartschool.edu', 'English Literature'),
            ('teacher_cs', 'Mr. Alex', 'Rodriguez', 'cs.teacher@smartschool.edu', 'Computer Science'),
        ]
        
        for username, first_name, last_name, email, subject_name in teacher_data:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': f'+1-555-{random.randint(1000, 9999)}',
                    'address': f'{random.randint(100, 999)} Scholar Rd, Academic City, AC {random.randint(10000, 99999)}',
                    'date_of_birth': f'19{random.randint(75, 90)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'role': 'teacher',
                    'is_active': True
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
                TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'employee_id': f"TCH{random.randint(1000, 9999)}",
                        'department': 'Academic',
                        'specialization': f'{subject_name} Education',
                        'qualification': random.choice(['M.Sc.', 'Ph.D.', 'M.A.', 'M.Tech.']),
                        'experience_years': random.randint(3, 15),
                    }
                )
        
        # Create student users
        student_names = [
            ('Alice', 'Johnson'), ('Bob', 'Smith'), ('Carol', 'Davis'), ('David', 'Wilson'),
            ('Emma', 'Brown'), ('Frank', 'Garcia'), ('Grace', 'Martinez'), ('Henry', 'Anderson'),
            ('Ivy', 'Thomas'), ('Jack', 'Taylor'), ('Kate', 'White'), ('Leo', 'Harris'),
            ('Mia', 'Clark'), ('Noah', 'Lewis'), ('Olivia', 'Walker')
        ]
        
        classrooms = list(Classroom.objects.all())
        grades = ['10th', '11th', '12th']
        
        for i, (first_name, last_name) in enumerate(student_names):
            username = f'student_{first_name.lower()}'
            grade = random.choice(grades)
            # Find classroom for this grade
            matching_classrooms = [c for c in classrooms if grade in c.grade]
            classroom = random.choice(matching_classrooms) if matching_classrooms else classrooms[0]
            
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{first_name.lower()}.{last_name.lower()}@student.smartschool.edu',
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': f'+1-555-{random.randint(3000, 3999)}',
                    'address': f'{random.randint(100, 999)} Student Ave, Academic City, AC {random.randint(10000, 99999)}',
                    'date_of_birth': f'200{random.randint(5, 7)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'role': 'student',
                    'is_active': True
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f"STU{random.randint(10000, 99999)}",
                        'roll_number': f"{i+1:02d}",
                        'grade': grade,
                        'classroom': classroom,
                        'admission_date': f"202{random.randint(2, 4)}-0{random.randint(1, 9)}-{random.randint(10, 28)}",
                        'parent_guardian_name': f"Mr. & Mrs. {last_name}",
                        'parent_guardian_phone': f"+1-555-{random.randint(4000, 4999)}",
                        'parent_guardian_email': f"{first_name.lower()}.parent@email.com",
                        'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
                        'medical_conditions': random.choice(['None', 'Asthma', 'Allergies', 'None', 'None'])
                    }
                )
        
        # Create some parent users
        parent_names = [('Robert', 'Johnson'), ('Linda', 'Smith'), ('Michael', 'Davis')]
        for first_name, last_name in parent_names:
            username = f'parent_{last_name.lower()}'
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'parent.{last_name.lower()}@email.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': f'+1-555-{random.randint(5000, 5999)}',
                    'address': f'{random.randint(100, 999)} Family St, Academic City, AC {random.randint(10000, 99999)}',
                    'date_of_birth': f'19{random.randint(70, 85)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'role': 'parent',
                    'is_active': True
                }
            )
            if created:
                user.set_password('parent123')
                user.save()
                ParentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'relationship': random.choice(['father', 'mother']),
                        'occupation': random.choice(['Engineer', 'Doctor', 'Teacher', 'Business Owner']),
                        'workplace': f"{random.choice(['Tech Corp', 'Medical Center', 'Local School', 'Business Inc'])}",
                    }
                )
        
        self.stdout.write('Created comprehensive user profiles')

    def create_attendance_data(self):
        """Create realistic attendance data"""
        teachers = CustomUser.objects.filter(role='teacher')
        classrooms = Classroom.objects.all()
        subjects = Subject.objects.all()
        
        # Create attendance sessions for the past 30 days
        for i in range(30):
            date = timezone.now() - timedelta(days=i)
            
            for classroom in classrooms:
                # Create 2-3 sessions per day per classroom
                for session_num in range(random.randint(2, 3)):
                    teacher = random.choice(teachers)
                    subject = random.choice(subjects)
                    
                    session_time = date.replace(
                        hour=random.randint(8, 15),
                        minute=random.choice([0, 30]),
                        second=0,
                        microsecond=0
                    )
                    
                    session, created = AttendanceSession.objects.get_or_create(
                        title=f"{subject.name} - {classroom.name}",
                        classroom=classroom,
                        subject=subject,
                        teacher=teacher,
                        start_time=session_time,
                        defaults={
                            'description': f"Regular {subject.name} class for {classroom.name}",
                            'attendance_type': 'subject',
                            'status': 'completed',
                            'duration_minutes': random.choice([45, 60, 90]),
                            'end_time': session_time + timedelta(minutes=random.choice([45, 60, 90]))
                        }
                    )
                    
                    if created:
                        # Create attendance records for students
                        students = CustomUser.objects.filter(
                            role='student',
                            student_profile__classroom=classroom
                        )
                        
                        for student in students:
                            # 85% present, 10% late, 5% absent
                            status = random.choices(
                                ['present', 'late', 'absent'],
                                weights=[85, 10, 5]
                            )[0]
                            
                            AttendanceRecord.objects.get_or_create(
                                session=session,
                                student=student,
                                defaults={
                                    'status': status,
                                    'marked_at': session_time + timedelta(minutes=random.randint(0, 15)),
                                    'marked_by': teacher,
                                    'notes': random.choice(['', 'On time', 'Participated well', 'Asked questions', ''])
                                }
                            )
        
        # Set custom total sessions for presentation
        students = CustomUser.objects.filter(role='student')
        admin_user = CustomUser.objects.filter(role='admin').first()
        
        for student in students:
            if hasattr(student, 'student_profile') and student.student_profile:
                total_sessions = random.randint(50, 65)  # Realistic semester total
                StudentTotalSessions.objects.get_or_create(
                    student=student,
                    classroom=student.student_profile.classroom,
                    defaults={
                        'total_sessions': total_sessions,
                        'created_by': admin_user,
                        'updated_by': admin_user
                    }
                )
        
        self.stdout.write('Created comprehensive attendance data')

    def create_grades_and_assignments(self):
        """Create grades and assignments"""
        try:
            students = CustomUser.objects.filter(role='student')
            subjects = Subject.objects.all()
            teachers = CustomUser.objects.filter(role='teacher')
            classrooms = Classroom.objects.all()
            
            # Create grades
            grade_types = ['assignment', 'quiz', 'exam', 'project', 'participation']
            
            for student in students:
                for subject in subjects:
                    # Create 8-12 grades per subject
                    for i in range(random.randint(8, 12)):
                        points_possible = random.choice([50, 75, 100])
                        points_earned = random.uniform(points_possible * 0.75, points_possible * 0.95)
                        
                        Grade.objects.get_or_create(
                            student=student,
                            subject=subject,
                            title=f"{random.choice(grade_types).title()} {i+1}",
                            grade_type=random.choice(grade_types),
                            defaults={
                                'points_earned': round(points_earned, 2),
                                'points_possible': points_possible,
                                'date_assigned': timezone.now() - timedelta(days=random.randint(1, 90)),
                                'date_due': timezone.now() - timedelta(days=random.randint(1, 60)),
                                'teacher': random.choice(teachers),
                                'comments': random.choice([
                                    'Excellent work!', 'Good effort', 'Well done', 
                                    'Shows improvement', 'Outstanding performance'
                                ])
                            }
                        )
            
            # Create assignments
            assignment_types = ['Research Paper', 'Lab Report', 'Problem Set', 'Essay', 'Project']
            
            for i in range(25):  # Create 25 assignments
                teacher = random.choice(teachers)
                subject = random.choice(subjects)
                classroom = random.choice(classrooms)
                
                due_date = timezone.now() + timedelta(days=random.randint(1, 30))
                
                assignment, created = Assignment.objects.get_or_create(
                    title=f"{random.choice(assignment_types)}: {subject.name} Topic {i+1}",
                    teacher=teacher,
                    subject=subject,
                    classroom=classroom,
                    defaults={
                        'description': f"Complete a comprehensive {random.choice(assignment_types).lower()} on the given topic. Include proper analysis and citations.",
                        'due_date': due_date,
                        'max_points': random.choice([50, 75, 100]),
                        'priority': random.choice(['low', 'medium', 'high']),
                        'status': 'published',
                        'allow_late_submission': random.choice([True, False]),
                        'late_penalty_percent': random.randint(5, 15)
                    }
                )
                
                if created:
                    # Create submissions
                    students = CustomUser.objects.filter(
                        role='student',
                        student_profile__classroom=classroom
                    )
                    
                    for student in students:
                        if random.random() < 0.75:  # 75% submission rate
                            AssignmentSubmission.objects.get_or_create(
                                assignment=assignment,
                                student=student,
                                defaults={
                                    'submission_text': f"This is my submission for {assignment.title}. I have completed the research and analysis as requested.",
                                    'status': random.choice(['submitted', 'graded', 'returned']),
                                    'grade': random.uniform(75, 95) if random.random() < 0.8 else None,
                                    'feedback': random.choice([
                                        'Great work!', 'Good effort', 'Excellent analysis',
                                        'Well done', 'Outstanding work'
                                    ]) if random.random() < 0.6 else '',
                                    'graded_by': teacher if random.random() < 0.7 else None
                                }
                            )
            
            self.stdout.write('Created grades and assignments')
        except Exception as e:
            self.stdout.write(f'Note: Some data creation skipped - {str(e)}')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 PRESENTATION DATA SUMMARY'))
        self.stdout.write('='*60)
        
        counts = {
            'Total Users': CustomUser.objects.count(),
            'Students': CustomUser.objects.filter(role='student').count(),
            'Teachers': CustomUser.objects.filter(role='teacher').count(),
            'Admins': CustomUser.objects.filter(role='admin').count(),
            'Parents': CustomUser.objects.filter(role='parent').count(),
            'Classrooms': Classroom.objects.count(),
            'Subjects': Subject.objects.count(),
            'Attendance Sessions': AttendanceSession.objects.count(),
            'Attendance Records': AttendanceRecord.objects.count(),
            'Total Sessions Records': StudentTotalSessions.objects.count(),
        }
        
        try:
            counts['Grades'] = Grade.objects.count()
            counts['Assignments'] = Assignment.objects.count()
            counts['Assignment Submissions'] = AssignmentSubmission.objects.count()
        except:
            pass
        
        for item, count in counts.items():
            self.stdout.write(f'{item:.<30} {count:>5}')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 PRESENTATION DATABASE IS READY!'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n' + self.style.WARNING('🔑 LOGIN CREDENTIALS:'))
        self.stdout.write('-'*50)
        self.stdout.write('👨‍💼 Admin: admin_principal / admin123')
        self.stdout.write('👩‍🏫 Teacher: teacher_math / teacher123')
        self.stdout.write('👨‍🎓 Student: student_alice / student123')
        self.stdout.write('👨‍👩‍👧‍👦 Parent: parent_johnson / parent123')
        self.stdout.write('-'*50)
        self.stdout.write('🌐 Access at: http://127.0.0.1:8000/')
        self.stdout.write('-'*50)