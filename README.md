Smart Classroom Management System
A Django-based web application for managing classroom activities: attendance, assignments, feedback, grades, and user roles (students, teachers, admins).
Features
•	User Management – Registration, login, role-based profiles
•	Attendance – Track sessions, mark/view totals
•	Assignments – Create, submit, grade
•	Feedback – Submit/respond to session feedback
•	Grades – Track grades with reports
•	Classrooms & Subjects – Manage classes/subjects
•	Admin Dashboard – Full access via Django admin
•	API Support – REST endpoints with Django REST Framework
Prerequisites
•	Python 3.8+ (tested with 3.13)
•	Git (for cloning)
•	Pip / Virtualenv
Setup
Clone repository:
git clone https://github.com/Panith3366/Smart-Classroom-Management-System-Django-.git
cd Smart-Classroom-Management-System-Django-
cd "Smart Classroom"
Create and activate virtual environment:
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Linux/Mac
Install dependencies:
pip install -r requirements.txt
pip install Pillow
Run migrations:
python manage.py makemigrations
python manage.py migrate
Create superuser:
python manage.py createsuperuser
Running the Project
Start server:
python manage.py runserver 127.0.0.1:8002
App → http://127.0.0.1:8002/
Login → /login/
Admin → /admin/
Database
Default: SQLite (db.sqlite3)
For MySQL:
CREATE DATABASE smart_classroom;
Update settings.py → DATABASES section, then run:
python manage.py migrate
Development
Run tests:
python manage.py test
Set DEBUG=False for production
Use collectstatic before deployment
Deployable to Heroku / AWS / Render
Contributing
1.	Fork the repo
2.	Create a feature branch
3.	Commit your changes
4.	Push to branch
5.	Open a Pull Request

