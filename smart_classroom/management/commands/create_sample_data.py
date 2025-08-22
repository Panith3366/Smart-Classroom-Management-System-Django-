from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser
from teacher.models import TeacherProfile, Assignment, Quiz
from subject.models import Subject, SubjectTeacher
from classroom.models import Classroom, Announcement
from datetime import date, datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for the Smart Classroom Management System'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample subjects
        subjects_data = [
            {'name': 'Mathematics', 'description': 'Advanced mathematics including algebra, geometry, and calculus'},
            {'name': 'English Literature', 'description': 'Study of classic and modern literature'},
            {'name': 'Physics', 'description': 'Fundamental principles of physics and mechanics'},
            {'name': 'Chemistry', 'description': 'Organic and inorganic chemistry'},
            {'name': 'History', 'description': 'World history and historical analysis'},
            {'name': 'Computer Science', 'description': 'Programming, algorithms, and computer systems'},
        ]

        subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_data['name'],
                defaults={'description': subject_data['description']}
            )
            subjects.append(subject)
            if created:
                self.stdout.write(f'Created subject: {subject.name}')

        # Create sample classrooms
        classrooms_data = [
            {'name': 'Class 10A', 'grade': '10'},
            {'name': 'Class 10B', 'grade': '10'},
            {'name': 'Class 11A', 'grade': '11'},
            {'name': 'Class 11B', 'grade': '11'},
            {'name': 'Class 12A', 'grade': '12'},
            {'name': 'Class 12B', 'grade': '12'},
        ]

        # First create a default teacher for classrooms
        default_teacher, created = CustomUser.objects.get_or_create(
            username='default_teacher',
            defaults={
                'email': 'default@example.com',
                'first_name': 'Default',
                'last_name': 'Teacher',
                'role': 'teacher'
            }
        )
        if created:
            default_teacher.set_password('teacher123')
            default_teacher.save()
            TeacherProfile.objects.get_or_create(user=default_teacher)

        classrooms = []
        for classroom_data in classrooms_data:
            classroom, created = Classroom.objects.get_or_create(
                name=classroom_data['name'],
                defaults={
                    'grade': classroom_data['grade'],
                    'teacher': default_teacher
                }
            )
            classrooms.append(classroom)
            if created:
                self.stdout.write(f'Created classroom: {classroom.name}')

        # Create sample teachers
        teachers_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_johnson', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
            {'username': 'sarah_wilson', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
            {'username': 'david_brown', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Brown'},
        ]

        teachers = []
        for teacher_data in teachers_data:
            teacher, created = CustomUser.objects.get_or_create(
                username=teacher_data['username'],
                defaults={
                    'email': teacher_data['email'],
                    'first_name': teacher_data['first_name'],
                    'last_name': teacher_data['last_name'],
                    'role': 'teacher'
                }
            )
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                TeacherProfile.objects.get_or_create(user=teacher)
                teachers.append(teacher)
                self.stdout.write(f'Created teacher: {teacher.first_name} {teacher.last_name}')

        # Create sample students
        students_data = [
            {'username': 'student1', 'email': 'student1@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'student2', 'email': 'student2@example.com', 'first_name': 'Bob', 'last_name': 'Williams'},
            {'username': 'student3', 'email': 'student3@example.com', 'first_name': 'Charlie', 'last_name': 'Davis'},
            {'username': 'student4', 'email': 'student4@example.com', 'first_name': 'Diana', 'last_name': 'Miller'},
            {'username': 'student5', 'email': 'student5@example.com', 'first_name': 'Eva', 'last_name': 'Garcia'},
        ]

        for student_data in students_data:
            student, created = CustomUser.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'role': 'student'
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(f'Created student: {student.first_name} {student.last_name}')

        # Create subject-teacher assignments
        if teachers and subjects and classrooms:
            for i, teacher in enumerate(teachers[:3]):  # Assign first 3 teachers
                for j, subject in enumerate(subjects[:2]):  # To first 2 subjects each
                    classroom = classrooms[i % len(classrooms)]
                    assignment, created = SubjectTeacher.objects.get_or_create(
                        subject=subject,
                        teacher=teacher,
                        classroom=classroom
                    )
                    if created:
                        self.stdout.write(f'Assigned {teacher.first_name} to teach {subject.name} in {classroom.name}')

        # Create sample assignments
        if subjects and classrooms:
            assignments_data = [
                {'subject': subjects[0], 'classroom': classrooms[0], 'due_date': date(2025, 8, 15)},
                {'subject': subjects[1], 'classroom': classrooms[1], 'due_date': date(2025, 8, 20)},
                {'subject': subjects[2], 'classroom': classrooms[2], 'due_date': date(2025, 8, 25)},
            ]

            for assignment_data in assignments_data:
                assignment, created = Assignment.objects.get_or_create(
                    subject=assignment_data['subject'],
                    classroom=assignment_data['classroom'],
                    defaults={'due_date': assignment_data['due_date']}
                )
                if created:
                    self.stdout.write(f'Created assignment for {assignment.subject.name} in {assignment.classroom.name}')

        # Create sample quizzes
        if subjects and classrooms:
            sample_questions = [
                {
                    'text': 'What is 2 + 2?',
                    'options': {'A': '3', 'B': '4', 'C': '5', 'D': '6'},
                    'correct_answer': 'B'
                },
                {
                    'text': 'What is the capital of France?',
                    'options': {'A': 'London', 'B': 'Berlin', 'C': 'Paris', 'D': 'Madrid'},
                    'correct_answer': 'C'
                }
            ]

            quizzes_data = [
                {'title': 'Math Quiz 1', 'subject': subjects[0], 'classroom': classrooms[0]},
                {'title': 'English Quiz 1', 'subject': subjects[1], 'classroom': classrooms[1]},
                {'title': 'Physics Quiz 1', 'subject': subjects[2], 'classroom': classrooms[2]},
            ]

            for quiz_data in quizzes_data:
                quiz, created = Quiz.objects.get_or_create(
                    title=quiz_data['title'],
                    subject=quiz_data['subject'],
                    classroom=quiz_data['classroom'],
                    defaults={'questions': sample_questions}
                )
                if created:
                    self.stdout.write(f'Created quiz: {quiz.title}')

        # Create sample announcements
        if classrooms:
            announcements_data = [
                {'classroom': classrooms[0], 'message': 'Welcome to the new semester! Please check your assignments.'},
                {'classroom': classrooms[1], 'message': 'Parent-teacher meeting scheduled for next week.'},
                {'classroom': classrooms[2], 'message': 'Science fair preparations begin next Monday.'},
            ]

            for announcement_data in announcements_data:
                announcement, created = Announcement.objects.get_or_create(
                    classroom=announcement_data['classroom'],
                    message=announcement_data['message']
                )
                if created:
                    self.stdout.write(f'Created announcement for {announcement.classroom.name}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write('You can now access the application at http://127.0.0.1:8000/')
        self.stdout.write('Default passwords by role:')
        self.stdout.write('  Admin: admin123')
        self.stdout.write('  Teacher: teacher123')
        self.stdout.write('  Student: student123')
        self.stdout.write('  Parent: parent123')