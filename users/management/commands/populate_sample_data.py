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
    help = 'Populate database with comprehensive sample data for presentation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        with transaction.atomic():
            # Create comprehensive sample data
            self.create_classrooms()
            self.create_subjects()
            self.create_users_with_profiles()
            self.create_attendance_data()
            self.create_grades_data()
            self.create_assignments_data()
            
        self.stdout.write(self.style.SUCCESS('✅ Sample data population completed successfully!'))
        self.print_summary()

    def clear_data(self):
        """Clear existing data"""
        models_to_clear = [
            AssignmentSubmission, Assignment, Grade,
            AttendanceRecord, AttendanceSession, StudentTotalSessions,
            StudentProfile, TeacherProfile, AdminProfile, ParentProfile,
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'Cleared {count} {model.__name__} records')

    def create_classrooms(self):
        """Create sample classrooms"""
        # First create a default teacher for classrooms
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
        
        classrooms_data = [
            {'name': 'Grade 10-A', 'grade': '10th'},
            {'name': 'Grade 10-B', 'grade': '10th'},
            {'name': 'Grade 11-A', 'grade': '11th'},
            {'name': 'Grade 11-B', 'grade': '11th'},
            {'name': 'Grade 12-A', 'grade': '12th'},
        ]
        
        for data in classrooms_data:
            classroom, created = Classroom.objects.get_or_create(
                name=data['name'],
                defaults={
                    'name': data['name'],
                    'grade': data['grade'],
                    'teacher': default_teacher
                }
            )
            if created:
                self.stdout.write(f'Created classroom: {classroom.name}')

    def create_subjects(self):
        """Create sample subjects"""
        subjects_data = [
            {'name': 'Mathematics', 'description': 'Advanced Mathematics including Calculus and Algebra'},
            {'name': 'Physics', 'description': 'Fundamental Physics with practical laboratory work'},
            {'name': 'Chemistry', 'description': 'Organic and Inorganic Chemistry with experiments'},
            {'name': 'Biology', 'description': 'Life Sciences and Human Biology'},
            {'name': 'English Literature', 'description': 'Classic and Modern Literature Analysis'},
            {'name': 'History', 'description': 'World History and Cultural Studies'},
            {'name': 'Computer Science', 'description': 'Programming and Computer Applications'},
            {'name': 'Economics', 'description': 'Micro and Macro Economics'},
        ]
        
        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created subject: {subject.name}')

    def create_users_with_profiles(self):
        """Create comprehensive user data with detailed profiles"""
        
        # Create detailed admin users
        admin_data = [
            {
                'username': 'admin_principal', 'email': 'principal@smartschool.edu',
                'first_name': 'Dr. Robert', 'last_name': 'Anderson',
                'phone_number': '+1-555-0101', 'address': '123 Education Ave, Academic City, AC 12345',
                'date_of_birth': '1975-03-15'
            },
            {
                'username': 'admin_vice', 'email': 'vice.principal@smartschool.edu',
                'first_name': 'Ms. Sarah', 'last_name': 'Thompson',
                'phone_number': '+1-555-0102', 'address': '456 Learning St, Academic City, AC 12346',
                'date_of_birth': '1980-07-22'
            }
        ]
        
        for data in admin_data:
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'address': data['address'],
                    'date_of_birth': data['date_of_birth'],
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
                        'position': 'Principal' if 'principal' in data['username'] else 'Vice Principal',
                        'employee_id': f"ADM{random.randint(1000, 9999)}",
                        'hire_date': '2020-01-15',
                        'office_location': 'Main Building, Floor 3',
                        'bio': f"Experienced educator with over 15 years in academic administration."
                    }
                )
                self.stdout.write(f'Created admin: {user.get_full_name()}')

        # Create detailed teacher users
        teachers_data = [
            {
                'username': 'teacher_math', 'email': 'math.teacher@smartschool.edu',
                'first_name': 'Dr. Michael', 'last_name': 'Johnson',
                'phone_number': '+1-555-0201', 'address': '789 Scholar Rd, Academic City, AC 12347',
                'date_of_birth': '1985-09-10',
                'subject': 'Mathematics', 'specialization': 'Advanced Calculus and Statistics'
            },
            {
                'username': 'teacher_physics', 'email': 'physics.teacher@smartschool.edu',
                'first_name': 'Dr. Emily', 'last_name': 'Davis',
                'phone_number': '+1-555-0202', 'address': '321 Science Blvd, Academic City, AC 12348',
                'date_of_birth': '1982-12-05', 'gender': 'female',
                'subject': 'Physics', 'specialization': 'Quantum Physics and Laboratory Research'
            },
            {
                'username': 'teacher_chemistry', 'email': 'chemistry.teacher@smartschool.edu',
                'first_name': 'Prof. David', 'last_name': 'Wilson',
                'phone_number': '+1-555-0203', 'address': '654 Research Ave, Academic City, AC 12349',
                'date_of_birth': '1978-04-18', 'gender': 'male',
                'subject': 'Chemistry', 'specialization': 'Organic Chemistry and Material Science'
            },
            {
                'username': 'teacher_english', 'email': 'english.teacher@smartschool.edu',
                'first_name': 'Ms. Jennifer', 'last_name': 'Brown',
                'phone_number': '+1-555-0204', 'address': '987 Literature Lane, Academic City, AC 12350',
                'date_of_birth': '1988-11-30', 'gender': 'female',
                'subject': 'English Literature', 'specialization': 'Modern Literature and Creative Writing'
            },
            {
                'username': 'teacher_cs', 'email': 'cs.teacher@smartschool.edu',
                'first_name': 'Mr. Alex', 'last_name': 'Rodriguez',
                'phone_number': '+1-555-0205', 'address': '147 Tech Street, Academic City, AC 12351',
                'date_of_birth': '1990-06-25', 'gender': 'male',
                'subject': 'Computer Science', 'specialization': 'AI and Machine Learning'
            }
        ]
        
        classrooms = list(Classroom.objects.all())
        subjects = list(Subject.objects.all())
        
        for data in teachers_data:
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'address': data['address'],
                    'date_of_birth': data['date_of_birth'],
                    'gender': data['gender'],
                    'role': 'teacher',
                    'is_active': True
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
                
                # Assign subjects and classrooms
                subject_obj = next((s for s in subjects if s.name == data['subject']), subjects[0])
                assigned_classrooms = random.sample(classrooms, random.randint(2, 4))
                
                teacher_profile, _ = TeacherProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'employee_id': f"TCH{random.randint(1000, 9999)}",
                        'department': 'Academic',
                        'specialization': data['specialization'],
                        'qualification': random.choice(['M.Sc.', 'Ph.D.', 'M.A.', 'M.Tech.']),
                        'experience_years': random.randint(3, 15),
                        'hire_date': f"202{random.randint(0, 3)}-0{random.randint(1, 9)}-{random.randint(10, 28)}",
                        'salary': random.randint(45000, 85000),
                        'office_location': f"Faculty Block, Room {random.randint(101, 350)}",
                        'bio': f"Passionate educator specializing in {data['specialization']} with extensive research background."
                    }
                )
                
                # Assign subjects and classrooms
                teacher_profile.subjects.add(subject_obj)
                for classroom in assigned_classrooms:
                    teacher_profile.classrooms.add(classroom)
                
                self.stdout.write(f'Created teacher: {user.get_full_name()}')

        # Create detailed student users
        students_data = [
            {
                'username': 'student_alice', 'email': 'alice.johnson@student.smartschool.edu',
                'first_name': 'Alice', 'last_name': 'Johnson',
                'phone_number': '+1-555-0301', 'address': '111 Student Ave, Academic City, AC 12352',
                'date_of_birth': '2006-03-15', 'gender': 'female',
                'grade': '10th', 'blood_group': 'A+', 'parent_name': 'Mr. & Mrs. Johnson'
            },
            {
                'username': 'student_bob', 'email': 'bob.smith@student.smartschool.edu',
                'first_name': 'Bob', 'last_name': 'Smith',
                'phone_number': '+1-555-0302', 'address': '222 Youth Street, Academic City, AC 12353',
                'date_of_birth': '2005-07-22', 'gender': 'male',
                'grade': '11th', 'blood_group': 'B+', 'parent_name': 'Mr. & Mrs. Smith'
            },
            {
                'username': 'student_carol', 'email': 'carol.davis@student.smartschool.edu',
                'first_name': 'Carol', 'last_name': 'Davis',
                'phone_number': '+1-555-0303', 'address': '333 Learning Lane, Academic City, AC 12354',
                'date_of_birth': '2006-11-08', 'gender': 'female',
                'grade': '10th', 'blood_group': 'O+', 'parent_name': 'Mr. & Mrs. Davis'
            },
            {
                'username': 'student_david', 'email': 'david.wilson@student.smartschool.edu',
                'first_name': 'David', 'last_name': 'Wilson',
                'phone_number': '+1-555-0304', 'address': '444 Scholar Road, Academic City, AC 12355',
                'date_of_birth': '2005-01-30', 'gender': 'male',
                'grade': '12th', 'blood_group': 'AB+', 'parent_name': 'Mr. & Mrs. Wilson'
            },
            {
                'username': 'student_emma', 'email': 'emma.brown@student.smartschool.edu',
                'first_name': 'Emma', 'last_name': 'Brown',
                'phone_number': '+1-555-0305', 'address': '555 Education Blvd, Academic City, AC 12356',
                'date_of_birth': '2006-09-12', 'gender': 'female',
                'grade': '10th', 'blood_group': 'A-', 'parent_name': 'Mr. & Mrs. Brown'
            },
            {
                'username': 'student_frank', 'email': 'frank.garcia@student.smartschool.edu',
                'first_name': 'Frank', 'last_name': 'Garcia',
                'phone_number': '+1-555-0306', 'address': '666 Knowledge Street, Academic City, AC 12357',
                'date_of_birth': '2005-05-18', 'gender': 'male',
                'grade': '11th', 'blood_group': 'B-', 'parent_name': 'Mr. & Mrs. Garcia'
            },
            {
                'username': 'student_grace', 'email': 'grace.martinez@student.smartschool.edu',
                'first_name': 'Grace', 'last_name': 'Martinez',
                'phone_number': '+1-555-0307', 'address': '777 Study Avenue, Academic City, AC 12358',
                'date_of_birth': '2006-12-03', 'gender': 'female',
                'grade': '10th', 'blood_group': 'O-', 'parent_name': 'Mr. & Mrs. Martinez'
            },
            {
                'username': 'student_henry', 'email': 'henry.anderson@student.smartschool.edu',
                'first_name': 'Henry', 'last_name': 'Anderson',
                'phone_number': '+1-555-0308', 'address': '888 Academic Circle, Academic City, AC 12359',
                'date_of_birth': '2005-08-14', 'gender': 'male',
                'grade': '11th', 'blood_group': 'A+', 'parent_name': 'Mr. & Mrs. Anderson'
            },
            {
                'username': 'student_ivy', 'email': 'ivy.thomas@student.smartschool.edu',
                'first_name': 'Ivy', 'last_name': 'Thomas',
                'phone_number': '+1-555-0309', 'address': '999 Campus Drive, Academic City, AC 12360',
                'date_of_birth': '2005-04-27', 'gender': 'female',
                'grade': '12th', 'blood_group': 'B+', 'parent_name': 'Mr. & Mrs. Thomas'
            },
            {
                'username': 'student_jack', 'email': 'jack.taylor@student.smartschool.edu',
                'first_name': 'Jack', 'last_name': 'Taylor',
                'phone_number': '+1-555-0310', 'address': '1010 University Way, Academic City, AC 12361',
                'date_of_birth': '2006-02-09', 'gender': 'male',
                'grade': '10th', 'blood_group': 'AB-', 'parent_name': 'Mr. & Mrs. Taylor'
            },
            {
                'username': 'student_kate', 'email': 'kate.white@student.smartschool.edu',
                'first_name': 'Kate', 'last_name': 'White',
                'phone_number': '+1-555-0311', 'address': '1111 College Street, Academic City, AC 12362',
                'date_of_birth': '2005-10-16', 'gender': 'female',
                'grade': '11th', 'blood_group': 'O+', 'parent_name': 'Mr. & Mrs. White'
            },
            {
                'username': 'student_leo', 'email': 'leo.harris@student.smartschool.edu',
                'first_name': 'Leo', 'last_name': 'Harris',
                'phone_number': '+1-555-0312', 'address': '1212 School Lane, Academic City, AC 12363',
                'date_of_birth': '2005-06-21', 'gender': 'male',
                'grade': '12th', 'blood_group': 'A-', 'parent_name': 'Mr. & Mrs. Harris'
            },
            {
                'username': 'student_mia', 'email': 'mia.clark@student.smartschool.edu',
                'first_name': 'Mia', 'last_name': 'Clark',
                'phone_number': '+1-555-0313', 'address': '1313 Education Plaza, Academic City, AC 12364',
                'date_of_birth': '2006-01-05', 'gender': 'female',
                'grade': '10th', 'blood_group': 'B+', 'parent_name': 'Mr. & Mrs. Clark'
            },
            {
                'username': 'student_noah', 'email': 'noah.lewis@student.smartschool.edu',
                'first_name': 'Noah', 'last_name': 'Lewis',
                'phone_number': '+1-555-0314', 'address': '1414 Learning Center, Academic City, AC 12365',
                'date_of_birth': '2005-11-28', 'gender': 'male',
                'grade': '11th', 'blood_group': 'AB+', 'parent_name': 'Mr. & Mrs. Lewis'
            },
            {
                'username': 'student_olivia', 'email': 'olivia.walker@student.smartschool.edu',
                'first_name': 'Olivia', 'last_name': 'Walker',
                'phone_number': '+1-555-0315', 'address': '1515 Knowledge Hub, Academic City, AC 12366',
                'date_of_birth': '2006-08-11', 'gender': 'female',
                'grade': '10th', 'blood_group': 'O-', 'parent_name': 'Mr. & Mrs. Walker'
            }
        ]
        
        for data in students_data:
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'address': data['address'],
                    'date_of_birth': data['date_of_birth'],
                    'gender': data['gender'],
                    'role': 'student',
                    'is_active': True
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                
                # Assign classroom based on grade
                grade_classroom_map = {
                    '10th': ['Grade 10-A', 'Grade 10-B'],
                    '11th': ['Grade 11-A', 'Grade 11-B'],
                    '12th': ['Grade 12-A']
                }
                
                possible_classrooms = grade_classroom_map.get(data['grade'], ['Grade 10-A'])
                classroom = Classroom.objects.filter(name__in=possible_classrooms).first()
                
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f"STU{random.randint(10000, 99999)}",
                        'roll_number': f"{random.randint(1, 50):02d}",
                        'grade': data['grade'],
                        'classroom': classroom,
                        'admission_date': f"202{random.randint(2, 4)}-0{random.randint(1, 9)}-{random.randint(10, 28)}",
                        'parent_guardian_name': data['parent_name'],
                        'parent_guardian_phone': f"+1-555-{random.randint(1000, 9999)}",
                        'parent_guardian_email': f"{data['first_name'].lower()}.parent@email.com",
                        'emergency_contact_name': f"Emergency Contact for {data['first_name']}",
                        'emergency_contact_phone': f"+1-555-{random.randint(1000, 9999)}",
                        'blood_group': data['blood_group'],
                        'medical_conditions': random.choice(['None', 'Asthma', 'Allergies to peanuts', 'None', 'None'])
                    }
                )
                self.stdout.write(f'Created student: {user.get_full_name()}')

        # Create parent users
        parent_data = [
            {
                'username': 'parent_johnson', 'email': 'parent.johnson@email.com',
                'first_name': 'Robert', 'last_name': 'Johnson',
                'phone_number': '+1-555-0401', 'address': '111 Student Ave, Academic City, AC 12352',
                'date_of_birth': '1975-05-20', 'gender': 'male',
                'student_name': 'Alice Johnson'
            },
            {
                'username': 'parent_smith', 'email': 'parent.smith@email.com',
                'first_name': 'Linda', 'last_name': 'Smith',
                'phone_number': '+1-555-0402', 'address': '222 Youth Street, Academic City, AC 12353',
                'date_of_birth': '1978-09-15', 'gender': 'female',
                'student_name': 'Bob Smith'
            },
            {
                'username': 'parent_davis', 'email': 'parent.davis@email.com',
                'first_name': 'Michael', 'last_name': 'Davis',
                'phone_number': '+1-555-0403', 'address': '333 Learning Lane, Academic City, AC 12354',
                'date_of_birth': '1973-12-08', 'gender': 'male',
                'student_name': 'Carol Davis'
            }
        ]
        
        for data in parent_data:
            user, created = CustomUser.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data['phone_number'],
                    'address': data['address'],
                    'date_of_birth': data['date_of_birth'],
                    'gender': data['gender'],
                    'role': 'parent',
                    'is_active': True
                }
            )
            if created:
                user.set_password('parent123')
                user.save()
                
                # Find the student
                student_first_name = data['student_name'].split()[0]
                student_profile = StudentProfile.objects.filter(
                    user__first_name=student_first_name
                ).first()
                
                parent_profile, _ = ParentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'relationship': random.choice(['father', 'mother']),
                        'occupation': random.choice(['Engineer', 'Doctor', 'Teacher', 'Business Owner', 'Manager']),
                        'workplace': f"{random.choice(['Tech Corp', 'Medical Center', 'Local School', 'Business Inc', 'Corporate Office'])}",
                        'work_phone': f"+1-555-{random.randint(2000, 2999)}"
                    }
                )
                
                if student_profile:
                    parent_profile.students.add(student_profile)
                
                self.stdout.write(f'Created parent: {user.get_full_name()}')

    def create_attendance_data(self):
        """Create comprehensive attendance data"""
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
                        # Create attendance records for students in this classroom
                        students = CustomUser.objects.filter(
                            role='student',
                            student_profile__classroom=classroom
                        )
                        
                        for student in students:
                            # 85% chance of being present, 10% late, 5% absent
                            status_choice = random.choices(
                                ['present', 'late', 'absent'],
                                weights=[85, 10, 5]
                            )[0]
                            
                            AttendanceRecord.objects.get_or_create(
                                session=session,
                                student=student,
                                defaults={
                                    'status': status_choice,
                                    'marked_at': session_time + timedelta(minutes=random.randint(0, 15)),
                                    'marked_by': teacher,
                                    'notes': random.choice(['', 'On time', 'Participated well', 'Asked good questions', ''])
                                }
                            )
        
        # Set custom total sessions for students
        students = CustomUser.objects.filter(role='student')
        for student in students:
            if hasattr(student, 'student_profile') and student.student_profile:
                total_sessions = random.randint(45, 60)  # Semester total
                StudentTotalSessions.objects.get_or_create(
                    student=student,
                    classroom=student.student_profile.classroom,
                    defaults={
                        'total_sessions': total_sessions,
                        'created_by': CustomUser.objects.filter(role='admin').first(),
                        'updated_by': CustomUser.objects.filter(role='admin').first()
                    }
                )
        
        self.stdout.write('Created comprehensive attendance data')

    def create_grades_data(self):
        """Create comprehensive grades data"""
        try:
            # Create grades for students
            students = CustomUser.objects.filter(role='student')
            subjects = Subject.objects.all()
            teachers = CustomUser.objects.filter(role='teacher')
            
            grade_types = ['assignment', 'quiz', 'exam', 'project', 'participation']
            
            for student in students:
                for subject in subjects:
                    # Create 8-12 grades per subject per student
                    for i in range(random.randint(8, 12)):
                        points_possible = random.choice([50, 75, 100])
                        points_earned = random.uniform(points_possible * 0.7, points_possible * 0.98)  # Good grades
                        
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
                                    'Shows improvement', 'Outstanding performance',
                                    'Great analysis', 'Keep up the good work'
                                ])
                            }
                        )
            
            self.stdout.write('Created comprehensive grades data')
        except Exception as e:
            self.stdout.write(f'Note: Grades creation skipped - {str(e)}')

    def create_assignments_data(self):
        """Create comprehensive assignments data"""
        try:
            teachers = CustomUser.objects.filter(role='teacher')
            subjects = Subject.objects.all()
            classrooms = Classroom.objects.all()
            
            assignment_types = [
                'Research Paper', 'Lab Report', 'Problem Set', 'Essay', 
                'Project', 'Presentation', 'Case Study', 'Analysis'
            ]
            
            for i in range(20):  # Create 20 assignments
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
                        'description': f"Complete a comprehensive {random.choice(assignment_types).lower()} on the given topic. Include proper citations and analysis.\n\nInstructions:\n1. Research the topic thoroughly\n2. Write a {random.randint(500, 2000)}-word analysis\n3. Include at least {random.randint(3, 8)} references\n4. Submit in PDF format",
                        'due_date': due_date,
                        'max_points': random.choice([50, 75, 100]),
                        'priority': random.choice(['low', 'medium', 'high']),
                        'status': 'published',
                        'allow_late_submission': random.choice([True, False]),
                        'late_penalty_percent': random.randint(5, 15)
                    }
                )
                
                if created:
                    # Create submissions for some students
                    students = CustomUser.objects.filter(
                        role='student',
                        student_profile__classroom=classroom
                    )
                    
                    for student in students:
                        # 70% chance of submission
                        if random.random() < 0.7:
                            submission_date = due_date - timedelta(days=random.randint(0, 5))
                            
                            submission, sub_created = AssignmentSubmission.objects.get_or_create(
                                assignment=assignment,
                                student=student,
                                defaults={
                                    'submission_text': f"This is my submission for {assignment.title}. I have researched the topic and provided detailed analysis as requested. The work includes comprehensive research, proper citations, and thorough analysis of the subject matter.",
                                    'status': random.choice(['submitted', 'graded', 'returned']),
                                    'grade': random.uniform(75, 95) if random.random() < 0.8 else None,
                                    'feedback': random.choice([
                                        'Great work! Well researched and clearly written.',
                                        'Good effort. Consider adding more examples.',
                                        'Excellent analysis. Very thorough.',
                                        'Well done. Minor formatting issues.',
                                        'Outstanding work. Exceeded expectations.'
                                    ]) if random.random() < 0.6 else '',
                                    'graded_by': teacher if random.random() < 0.7 else None,
                                    'graded_at': timezone.now() - timedelta(days=random.randint(1, 10)) if random.random() < 0.7 else None
                                }
                            )
            
            self.stdout.write('Created comprehensive assignments data')
        except Exception as e:
            self.stdout.write(f'Note: Assignments creation skipped - {str(e)}')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 DATA POPULATION SUMMARY'))
        self.stdout.write('='*60)
        
        # Count all data
        counts = {
            'Users': CustomUser.objects.count(),
            'Students': CustomUser.objects.filter(role='student').count(),
            'Teachers': CustomUser.objects.filter(role='teacher').count(),
            'Admins': CustomUser.objects.filter(role='admin').count(),
            'Parents': CustomUser.objects.filter(role='parent').count(),
            'Classrooms': Classroom.objects.count(),
            'Subjects': Subject.objects.count(),
            'Attendance Sessions': AttendanceSession.objects.count(),
            'Attendance Records': AttendanceRecord.objects.count(),
        }
        
        try:
            counts['Grades'] = Grade.objects.count()
        except:
            pass
            
        try:
            counts['Assignments'] = Assignment.objects.count()
            counts['Assignment Submissions'] = AssignmentSubmission.objects.count()
        except:
            pass
        
        for item, count in counts.items():
            self.stdout.write(f'{item:.<25} {count:>5}')
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Your presentation database is ready!'))
        self.stdout.write('='*60)
        
        # Print login credentials
        self.stdout.write('\n' + self.style.WARNING('🔑 LOGIN CREDENTIALS:'))
        self.stdout.write('-'*40)
        self.stdout.write('Admin: admin_principal / admin123')
        self.stdout.write('Teacher: teacher_math / teacher123')
        self.stdout.write('Student: student_alice / student123')
        self.stdout.write('Parent: parent_johnson / parent123')
        self.stdout.write('-'*40)