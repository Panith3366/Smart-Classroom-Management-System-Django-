---
description: Repository Information Overview
alwaysApply: true
---

# Smart Classroom Management System Information

## Summary
A comprehensive Django-based classroom management system with features for attendance tracking, assignment management, grading, feedback, and user management with different roles (admin, teacher, student, parent).

## Structure
- **attendance/**: Attendance tracking functionality
- **assignments/**: Assignment management module
- **classroom/**: Classroom management features
- **feedback/**: Student feedback system
- **grades/**: Grading and assessment module
- **smart_classroom/**: Main project configuration
- **static/**: Static files (CSS, JS, images)
- **subject/**: Subject management module
- **teacher/**: Teacher management functionality
- **templates/**: HTML templates for the web interface
- **tests/**: Test files for API and functionality testing
- **users/**: User management with custom user model

## Language & Runtime
**Language**: Python
**Version**: Django 4.x/5.x
**Build System**: Django's built-in management system
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- Django (>=4.0,<5.0)
- djangorestframework
- djangorestframework-simplejwt

## Database
**Engine**: SQLite3 (development)
**Configuration**: Located in smart_classroom/settings.py
**Models**: Distributed across app directories (users, classroom, etc.)

## Build & Installation
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create sample data (optional)
python create_sample_data.py

# Start development server
python manage.py runserver
```

## API
**Authentication**: JWT (JSON Web Tokens)
**Endpoints**:
- /api/users/ - User management
- /api/classroom/ - Classroom operations
- /api/teacher/ - Teacher management
- /api/subject/ - Subject management

## Testing
**Framework**: Django's TestCase and APITestCase
**Test Files**: 
- tests/test_api.py - API tests
- test_views.py - View tests
- test_attendance.py - Attendance module tests
- test_system.py - System integration tests

**Run Command**:
```bash
python manage.py test
```

## User Roles
- **Admin**: System administration and user management
- **Teacher**: Manage classes, assignments, grades
- **Student**: View assignments, submit work, check grades
- **Parent**: Monitor student progress and attendance