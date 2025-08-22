from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random

from users.models import CustomUser, StudentProfile, TeacherProfile
from classroom.models import Classroom, Announcement
from subject.models import Subject, SubjectTeacher
from attendance.models import AttendanceSession, AttendanceRecord


class Command(BaseCommand):
    help = 'Add extra presentation data - announcements, subject assignments, etc.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Adding presentation extras...'))
        
        with transaction.atomic():
            self.create_announcements()
            self.assign_subjects_to_teachers()
            self.update_profile_details()
            
        self.stdout.write(self.style.SUCCESS('✅ Presentation extras added!'))

    def create_announcements(self):
        """Create classroom announcements"""
        classrooms = Classroom.objects.all()
        
        announcement_templates = [
            "📚 Reminder: Assignment due next Friday. Please submit on time!",
            "🧪 Lab session scheduled for tomorrow. Bring your safety goggles.",
            "📝 Quiz on Chapter 5 this Thursday. Review your notes!",
            "🎉 Congratulations to all students for excellent performance in midterms!",
            "📖 New textbooks available in the library. Check them out!",
            "⚠️ Class timing changed to 10:30 AM for this week only.",
            "🏆 Science fair registration open. Submit your project ideas!",
            "📅 Parent-teacher meeting scheduled for next month.",
            "💡 Study group sessions available every evening in Room 201.",
            "🎯 Mock exams start next week. Prepare well!"
        ]
        
        for classroom in classrooms:
            # Create 3-5 announcements per classroom
            for i in range(random.randint(3, 5)):
                announcement_text = random.choice(announcement_templates)
                created_date = timezone.now() - timedelta(days=random.randint(1, 15))
                
                Announcement.objects.get_or_create(
                    classroom=classroom,
                    message=announcement_text,
                    defaults={'created_at': created_date}
                )
        
        self.stdout.write('Created classroom announcements')

    def assign_subjects_to_teachers(self):
        """Assign subjects to teachers and classrooms"""
        teachers = CustomUser.objects.filter(role='teacher')
        subjects = Subject.objects.all()
        classrooms = Classroom.objects.all()
        
        # Subject-teacher mapping based on specialization
        subject_teacher_map = {
            'Mathematics': ['teacher_math'],
            'Physics': ['teacher_physics'],
            'Chemistry': ['teacher_chemistry'],
            'English Literature': ['teacher_english'],
            'Computer Science': ['teacher_cs'],
            'Biology': ['teacher_physics', 'teacher_chemistry'],  # Can be taught by science teachers
            'History': ['teacher_english'],  # Can be taught by humanities teachers
            'Economics': ['teacher_math', 'teacher_english']  # Can be taught by multiple teachers
        }
        
        for subject in subjects:
            # Get preferred teachers for this subject
            preferred_usernames = subject_teacher_map.get(subject.name, [])
            if preferred_usernames:
                preferred_teachers = [t for t in teachers if t.username in preferred_usernames]
            else:
                preferred_teachers = [random.choice(teachers)]
            
            # Assign to 2-3 classrooms per subject
            assigned_classrooms = random.sample(list(classrooms), min(3, len(classrooms)))
            
            for classroom in assigned_classrooms:
                teacher = random.choice(preferred_teachers)
                SubjectTeacher.objects.get_or_create(
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom
                )
        
        self.stdout.write('Assigned subjects to teachers and classrooms')

    def update_profile_details(self):
        """Add more detailed information to profiles"""
        
        # Update teacher profiles with more details
        teachers = TeacherProfile.objects.all()
        
        for teacher_profile in teachers:
            # Update emergency contact if not set
            if not teacher_profile.emergency_contact_name:
                teacher_profile.emergency_contact_name = f"Emergency Contact for {teacher_profile.user.first_name}"
            
            if not teacher_profile.emergency_contact_phone:
                teacher_profile.emergency_contact_phone = f"+1-555-{random.randint(7000, 7999)}"
            
            # Ensure hire_date is set
            if not teacher_profile.hire_date:
                teacher_profile.hire_date = f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            # Ensure salary is set
            if not teacher_profile.salary:
                teacher_profile.salary = random.randint(45000, 85000)
            
            # Ensure qualification is set
            if not teacher_profile.qualification:
                teacher_profile.qualification = random.choice(['M.Sc.', 'Ph.D.', 'M.A.', 'M.Tech.', 'B.Ed.', 'M.Ed.'])
            
            teacher_profile.save()
        
        # Update student profiles with more details
        students = StudentProfile.objects.all()
        
        for student_profile in students:
            # Update emergency contact if not set
            if not student_profile.emergency_contact_name:
                student_profile.emergency_contact_name = f"Emergency Contact for {student_profile.user.first_name}"
            
            if not student_profile.emergency_contact_phone:
                student_profile.emergency_contact_phone = f"+1-555-{random.randint(6000, 6999)}"
            
            # Update medical conditions if not set
            if not student_profile.medical_conditions:
                student_profile.medical_conditions = random.choice([
                    'None', 'Mild asthma', 'Food allergies (nuts)', 'None', 'None', 
                    'Seasonal allergies', 'None', 'Lactose intolerant'
                ])
            
            student_profile.save()
        
        self.stdout.write('Updated profile details')

    def print_extras_summary(self):
        """Print summary of extras added"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 EXTRAS SUMMARY'))
        self.stdout.write('='*50)
        
        counts = {
            'Announcements': Announcement.objects.count(),
            'Subject-Teacher Assignments': SubjectTeacher.objects.count(),
            'Updated Teacher Profiles': TeacherProfile.objects.exclude(emergency_contact_name='').count(),
            'Updated Student Profiles': StudentProfile.objects.exclude(emergency_contact_name='').count(),
        }
        
        for item, count in counts.items():
            self.stdout.write(f'{item:.<35} {count:>5}')
        
        self.stdout.write('='*50)