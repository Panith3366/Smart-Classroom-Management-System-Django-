from django.core.management.base import BaseCommand
from django.db import transaction
import random

from users.models import CustomUser, StudentProfile, TeacherProfile
from classroom.models import Classroom


class Command(BaseCommand):
    help = 'Fix and complete all user profiles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Fixing user profiles...'))
        
        with transaction.atomic():
            self.fix_student_profiles()
            self.fix_teacher_profiles()
            self.assign_students_to_classrooms()
            
        self.stdout.write(self.style.SUCCESS('✅ All profiles fixed!'))

    def fix_student_profiles(self):
        """Ensure all student profiles are complete"""
        students = CustomUser.objects.filter(role='student')
        classrooms = list(Classroom.objects.all())
        
        for student in students:
            profile, created = StudentProfile.objects.get_or_create(
                user=student,
                defaults={
                    'student_id': f"STU{random.randint(10000, 99999)}",
                    'roll_number': f"{random.randint(1, 50):02d}",
                    'grade': random.choice(['10th', '11th', '12th']),
                    'classroom': random.choice(classrooms) if classrooms else None,
                    'admission_date': f"202{random.randint(2, 4)}-0{random.randint(1, 9)}-{random.randint(10, 28)}",
                    'parent_guardian_name': f"Mr. & Mrs. {student.last_name}",
                    'parent_guardian_phone': f"+1-555-{random.randint(4000, 4999)}",
                    'parent_guardian_email': f"{student.first_name.lower()}.parent@email.com",
                    'emergency_contact_name': f"Emergency Contact for {student.first_name}",
                    'emergency_contact_phone': f"+1-555-{random.randint(6000, 6999)}",
                    'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
                    'medical_conditions': random.choice(['None', 'Mild asthma', 'Food allergies', 'None', 'None'])
                }
            )
            
            # Update existing profiles that might be incomplete
            if not created:
                if not profile.student_id:
                    profile.student_id = f"STU{random.randint(10000, 99999)}"
                if not profile.parent_guardian_name:
                    profile.parent_guardian_name = f"Mr. & Mrs. {student.last_name}"
                if not profile.parent_guardian_phone:
                    profile.parent_guardian_phone = f"+1-555-{random.randint(4000, 4999)}"
                if not profile.parent_guardian_email:
                    profile.parent_guardian_email = f"{student.first_name.lower()}.parent@email.com"
                if not profile.emergency_contact_name:
                    profile.emergency_contact_name = f"Emergency Contact for {student.first_name}"
                if not profile.emergency_contact_phone:
                    profile.emergency_contact_phone = f"+1-555-{random.randint(6000, 6999)}"
                if not profile.grade:
                    profile.grade = random.choice(['10th', '11th', '12th'])
                if not profile.classroom and classrooms:
                    profile.classroom = random.choice(classrooms)
                if not profile.blood_group:
                    profile.blood_group = random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-'])
                if not profile.medical_conditions:
                    profile.medical_conditions = random.choice(['None', 'Mild asthma', 'Food allergies', 'None'])
                
                profile.save()
        
        self.stdout.write('Fixed student profiles')

    def fix_teacher_profiles(self):
        """Ensure all teacher profiles are complete"""
        teachers = CustomUser.objects.filter(role='teacher')
        
        for teacher in teachers:
            profile, created = TeacherProfile.objects.get_or_create(
                user=teacher,
                defaults={
                    'employee_id': f"TCH{random.randint(1000, 9999)}",
                    'department': 'Academic',
                    'qualification': random.choice(['M.Sc.', 'Ph.D.', 'M.A.', 'M.Tech.', 'B.Ed.', 'M.Ed.']),
                    'experience_years': random.randint(3, 15),
                    'specialization': f"{random.choice(['Mathematics', 'Science', 'English', 'Computer Science'])} Education",
                    'hire_date': f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    'salary': random.randint(45000, 85000),
                    'emergency_contact_name': f"Emergency Contact for {teacher.first_name}",
                    'emergency_contact_phone': f"+1-555-{random.randint(7000, 7999)}"
                }
            )
            
            # Update existing profiles that might be incomplete
            if not created:
                if not profile.employee_id:
                    profile.employee_id = f"TCH{random.randint(1000, 9999)}"
                if not profile.qualification:
                    profile.qualification = random.choice(['M.Sc.', 'Ph.D.', 'M.A.', 'M.Tech.', 'B.Ed.', 'M.Ed.'])
                if not profile.specialization:
                    profile.specialization = f"{random.choice(['Mathematics', 'Science', 'English', 'Computer Science'])} Education"
                if not profile.emergency_contact_name:
                    profile.emergency_contact_name = f"Emergency Contact for {teacher.first_name}"
                if not profile.emergency_contact_phone:
                    profile.emergency_contact_phone = f"+1-555-{random.randint(7000, 7999)}"
                if not profile.department:
                    profile.department = 'Academic'
                if not profile.salary:
                    profile.salary = random.randint(45000, 85000)
                
                profile.save()
        
        self.stdout.write('Fixed teacher profiles')

    def assign_students_to_classrooms(self):
        """Ensure all students are assigned to classrooms"""
        students = CustomUser.objects.filter(role='student')
        classrooms = list(Classroom.objects.all())
        
        if not classrooms:
            self.stdout.write('No classrooms available for assignment')
            return
        
        for student in students:
            if hasattr(student, 'student_profile') and student.student_profile:
                if not student.student_profile.classroom:
                    student.student_profile.classroom = random.choice(classrooms)
                    student.student_profile.save()
        
        self.stdout.write('Assigned students to classrooms')