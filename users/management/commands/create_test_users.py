from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import AdminProfile, TeacherProfile, StudentProfile, ParentProfile
from classroom.models import Classroom

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for all roles'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@school.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'phone_number': '+1234567890',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        
        # Create teacher user
        teacher_user, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher1@school.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'teacher',
                'phone_number': '+1234567891',
            }
        )
        if created:
            teacher_user.set_password('teacher123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created teacher user: {teacher_user.username}'))
            
            # Update teacher profile
            if hasattr(teacher_user, 'teacher_profile'):
                teacher_profile = teacher_user.teacher_profile
                teacher_profile.department = 'Mathematics'
                teacher_profile.qualification = 'M.Sc. Mathematics'
                teacher_profile.experience_years = 5
                teacher_profile.specialization = 'Algebra and Calculus'
                teacher_profile.save()
        
        # Create student user
        student_user, created = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'student1@school.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'student',
                'phone_number': '+1234567892',
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created student user: {student_user.username}'))
            
            # Update student profile
            if hasattr(student_user, 'student_profile'):
                student_profile = student_user.student_profile
                student_profile.roll_number = 'STU001'
                student_profile.grade = '10th'
                student_profile.parent_guardian_name = 'Robert Johnson'
                student_profile.parent_guardian_phone = '+1234567893'
                student_profile.parent_guardian_email = 'robert.johnson@email.com'
                student_profile.blood_group = 'A+'
                student_profile.save()
        
        # Create parent user
        parent_user, created = User.objects.get_or_create(
            username='parent1',
            defaults={
                'email': 'parent1@email.com',
                'first_name': 'Robert',
                'last_name': 'Johnson',
                'role': 'parent',
                'phone_number': '+1234567893',
            }
        )
        if created:
            parent_user.set_password('parent123')
            parent_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created parent user: {parent_user.username}'))
            
            # Update parent profile and link to student
            if hasattr(parent_user, 'parent_profile') and hasattr(student_user, 'student_profile'):
                parent_profile = parent_user.parent_profile
                parent_profile.relationship = 'father'
                parent_profile.occupation = 'Engineer'
                parent_profile.workplace = 'Tech Corp'
                parent_profile.save()
                parent_profile.students.add(student_user.student_profile)
        
        # Create a classroom if it doesn't exist
        classroom, created = Classroom.objects.get_or_create(
            name='Class 10A',
            defaults={
                'grade': '10th',
                'teacher': teacher_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created classroom: {classroom.name}'))
        
        # Assign student to classroom
        if hasattr(student_user, 'student_profile'):
            student_profile = student_user.student_profile
            student_profile.classroom = classroom
            student_profile.save()
            self.stdout.write(self.style.SUCCESS(f'Assigned student to classroom: {classroom.name}'))
        
        self.stdout.write(self.style.SUCCESS('Test users created successfully!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Teacher: teacher1 / teacher123')
        self.stdout.write('Student: student1 / student123')
        self.stdout.write('Parent: parent1 / parent123')
        self.stdout.write(self.style.WARNING('Student ID for parent access: Check the student profile'))