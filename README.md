🎓 Smart Classroom Management System

A Django-powered web application for managing classroom activities 📚, including attendance ✅, assignments 📝, feedback 💬, grades 🏆, and user roles 👨‍🏫👩‍🎓👨‍💻.




✨ Features

🔑 User Management – Registration, login, profiles (students 👩‍🎓, teachers 👨‍🏫, admins 👑)
📅 Attendance – Track sessions, mark attendance, view totals
📝 Assignments – Create, submit, grade assignments
💬 Feedback – Submit/respond to session feedback
🏆 Grades – Manage & view student grades
🏫 Classrooms & Subjects – Organize classes & subjects
📊 Admin Dashboard – Full access via Django admin
🔗 API Support – REST endpoints with Django REST Framework

📸 Screenshots
🔐 Login Page

📊 Student Dashboard

👨‍🏫 Teacher Panel

🏆 Grade Analytics

⚙️ Prerequisites

🐍 Python 3.8+ (tested up to 3.13)

🌐 Git (for cloning)

🚀 Setup
# Clone repo
git clone https://github.com/Panith3366/Smart-Classroom-Management-System-Django-.git
cd Smart-Classroom-Management-System-Django-
cd "Smart Classroom"

# Create venv
python -m venv venv
venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
pip install Pillow

# Migrate DB
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

▶️ Running the Project
# Run server
python manage.py runserver 127.0.0.1:8002


📍 Access → http://127.0.0.1:8002/
🔑 Login → /login/
👑 Admin → /admin/

🗄️ Database

Default → SQLite (db.sqlite3)

For MySQL:

CREATE DATABASE smart_classroom;


Update settings.py → DATABASES and run:

python manage.py migrate

🤝 Contributing

🍴 Fork it

🌱 Create feature branch

💾 Commit changes

📤 Push branch

🔁 Submit Pull Request

📌 Future Enhancements

✨ OTP/email login 🔑
📱 Mobile app with Django REST + Flutter/React Native
📊 AI-powered analytics for performance tracking

🔥 “Where teaching meets technology — fueling curiosity, shaping the future.”
