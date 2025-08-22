#!/usr/bin/env python
"""
Script to populate initial data for attendance and feedback systems
Run this after setting up the database
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')
django.setup()

from feedback.models import FeedbackCategory, FeedbackTemplate
from django.contrib.auth import get_user_model
from users.models import CustomUser, AdminProfile, TeacherProfile, StudentProfile, ParentProfile

User = get_user_model()

def create_default_users():
    """Create default users with specific passwords for each role"""
    print("Creating default users with specific passwords...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created admin user: admin / admin123")
    else:
        print("Admin user already exists")
    
    # Create teacher user
    teacher_user, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'email': 'teacher@example.com',
            'first_name': 'Teacher',
            'last_name': 'User',
            'role': 'teacher'
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        # Create teacher profile if it doesn't exist
        TeacherProfile.objects.get_or_create(user=teacher_user)
        print("Created teacher user: teacher / teacher123")
    else:
        print("Teacher user already exists")
    
    # Create student user
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@example.com',
            'first_name': 'Student',
            'last_name': 'User',
            'role': 'student'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
        # Create student profile if it doesn't exist
        StudentProfile.objects.get_or_create(user=student_user)
        print("Created student user: student / student123")
    else:
        print("Student user already exists")
    
    # Create parent user
    parent_user, created = User.objects.get_or_create(
        username='parent',
        defaults={
            'email': 'parent@example.com',
            'first_name': 'Parent',
            'last_name': 'User',
            'role': 'parent'
        }
    )
    if created:
        parent_user.set_password('parent123')
        parent_user.save()
        # Create parent profile if it doesn't exist
        ParentProfile.objects.get_or_create(user=parent_user)
        print("Created parent user: parent / parent123")
    else:
        print("Parent user already exists")

def create_feedback_categories():
    """Create initial feedback categories"""
    categories = [
        {
            'name': 'Course Evaluation',
            'description': 'Feedback about course content, structure, and delivery',
            'icon': 'fas fa-book-open',
            'color': '#4facfe'
        },
        {
            'name': 'Teacher Performance',
            'description': 'Feedback about teaching methods and instructor effectiveness',
            'icon': 'fas fa-chalkboard-teacher',
            'color': '#43e97b'
        },
        {
            'name': 'Student Experience',
            'description': 'General student experience and satisfaction feedback',
            'icon': 'fas fa-user-graduate',
            'color': '#fa709a'
        },
        {
            'name': 'Peer Review',
            'description': 'Collaborative feedback between students',
            'icon': 'fas fa-users',
            'color': '#667eea'
        },
        {
            'name': 'Self Assessment',
            'description': 'Student self-reflection and assessment',
            'icon': 'fas fa-mirror',
            'color': '#f093fb'
        },
        {
            'name': 'Assignment Feedback',
            'description': 'Feedback on assignments and projects',
            'icon': 'fas fa-tasks',
            'color': '#ffeaa7'
        }
    ]
    
    created_count = 0
    for cat_data in categories:
        category, created = FeedbackCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon'],
                'color': cat_data['color']
            }
        )
        if created:
            created_count += 1
            print(f"Created category: {category.name}")
    
    print(f"Created {created_count} new feedback categories")

def create_feedback_templates():
    """Create initial feedback templates"""
    # Get categories
    course_eval = FeedbackCategory.objects.get(name='Course Evaluation')
    teacher_perf = FeedbackCategory.objects.get(name='Teacher Performance')
    student_exp = FeedbackCategory.objects.get(name='Student Experience')
    
    templates = [
        {
            'title': 'Mid-term Course Evaluation',
            'description': 'Comprehensive mid-term evaluation of course progress and content',
            'template_type': 'teacher_to_student',
            'category': course_eval,
            'questions': [
                {
                    'type': 'rating',
                    'question': 'How would you rate the course content so far?',
                    'required': True,
                    'scale': 5
                },
                {
                    'type': 'multiple_choice',
                    'question': 'Which teaching method has been most effective for you?',
                    'options': ['Lectures', 'Practical exercises', 'Group discussions', 'Online resources'],
                    'required': True
                },
                {
                    'type': 'text',
                    'question': 'What topics would you like to see covered in more detail?',
                    'required': False
                },
                {
                    'type': 'scale',
                    'question': 'How likely are you to recommend this course to other students?',
                    'scale': 10,
                    'required': True
                }
            ]
        },
        {
            'title': 'Teacher Performance Review',
            'description': 'Evaluate teaching effectiveness and classroom management',
            'template_type': 'student_to_teacher',
            'category': teacher_perf,
            'questions': [
                {
                    'type': 'rating',
                    'question': 'How clear are the teacher\'s explanations?',
                    'required': True,
                    'scale': 5
                },
                {
                    'type': 'yes_no',
                    'question': 'Does the teacher encourage student participation?',
                    'required': True
                },
                {
                    'type': 'text',
                    'question': 'What does the teacher do well?',
                    'required': False
                },
                {
                    'type': 'text',
                    'question': 'What could the teacher improve?',
                    'required': False
                }
            ]
        },
        {
            'title': 'Student Satisfaction Survey',
            'description': 'General satisfaction and experience feedback',
            'template_type': 'teacher_to_student',
            'category': student_exp,
            'questions': [
                {
                    'type': 'emoji',
                    'question': 'How do you feel about your learning experience?',
                    'required': True
                },
                {
                    'type': 'rating',
                    'question': 'Rate the classroom environment',
                    'required': True,
                    'scale': 5
                },
                {
                    'type': 'multiple_choice',
                    'question': 'What motivates you most in learning?',
                    'options': ['Interactive activities', 'Clear explanations', 'Practical examples', 'Group work', 'Individual challenges'],
                    'required': True
                },
                {
                    'type': 'text',
                    'question': 'Any additional comments or suggestions?',
                    'required': False
                }
            ]
        }
    ]
    
    # We'll need to create a superuser first to assign as template creator
    # Try to get an existing superuser or use the default admin user
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.get(username='admin')
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin',
                is_superuser=True,
                is_staff=True
            )
            print("Created default admin user: admin/admin123")
    except Exception as e:
        print(f"Could not create admin user: {e}")
        return
    
    created_count = 0
    for template_data in templates:
        template, created = FeedbackTemplate.objects.get_or_create(
            title=template_data['title'],
            defaults={
                'description': template_data['description'],
                'template_type': template_data['template_type'],
                'category': template_data['category'],
                'questions': template_data['questions'],
                'created_by': admin_user,
                'is_public': True
            }
        )
        if created:
            created_count += 1
            print(f"Created template: {template.title}")
    
    print(f"Created {created_count} new feedback templates")

def main():
    print("Populating initial data for Attendance and Feedback systems...")
    print("=" * 60)
    
    try:
        create_default_users()
        print()
        create_feedback_categories()
        print()
        create_feedback_templates()
        print()
        print("✅ Data population completed successfully!")
        print("\nDefault users created with specific passwords:")
        print("- Admin: admin / admin123")
        print("- Teacher: teacher / teacher123")
        print("- Student: student / student123")
        print("- Parent: parent / parent123")
        print("\nYou can now:")
        print("1. Access the attendance dashboard at /attendance/")
        print("2. Access the feedback dashboard at /feedback/")
        print("3. Create new sessions using the advanced interfaces")
        
    except Exception as e:
        print(f"❌ Error during data population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
