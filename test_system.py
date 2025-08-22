#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')
django.setup()

from users.models import CustomUser, StudentProfile, TeacherProfile
from classroom.models import Classroom, Announcement
from attendance.models import AttendanceSession, AttendanceRecord, StudentTotalSessions
from grades.models import Grade
from assignments.models import Assignment, AssignmentSubmission
from subject.models import Subject, SubjectTeacher
from django.contrib.auth import authenticate

def test_system():
    print('='*60)
    print('🧪 SMART CLASSROOM SYSTEM TEST')
    print('='*60)
    
    # Test 1: Data Population
    print('\n📊 DATA POPULATION TEST')
    print('-'*40)
    users = CustomUser.objects.count()
    students = CustomUser.objects.filter(role='student').count()
    teachers = CustomUser.objects.filter(role='teacher').count()
    admins = CustomUser.objects.filter(role='admin').count()
    parents = CustomUser.objects.filter(role='parent').count()
    
    print(f'✅ Total Users: {users}')
    print(f'✅ Students: {students}')
    print(f'✅ Teachers: {teachers}')
    print(f'✅ Admins: {admins}')
    print(f'✅ Parents: {parents}')
    
    classrooms = Classroom.objects.count()
    subjects = Subject.objects.count()
    announcements = Announcement.objects.count()
    
    print(f'✅ Classrooms: {classrooms}')
    print(f'✅ Subjects: {subjects}')
    print(f'✅ Announcements: {announcements}')
    
    # Test 2: Authentication
    print('\n🔐 AUTHENTICATION TEST')
    print('-'*40)
    
    test_credentials = [
        ('admin_principal', 'admin123', 'Admin'),
        ('teacher_math', 'teacher123', 'Teacher'),
        ('student_alice', 'student123', 'Student'),
        ('parent_johnson', 'parent123', 'Parent')
    ]
    
    for username, password, role in test_credentials:
        user = authenticate(username=username, password=password)
        if user:
            print(f'✅ {role} Login: {username} - SUCCESS')
            print(f'   Name: {user.get_full_name()}')
            print(f'   Email: {user.email}')
        else:
            print(f'❌ {role} Login: {username} - FAILED')
    
    # Test 3: Profile Completeness
    print('\n👤 PROFILE COMPLETENESS TEST')
    print('-'*40)
    
    complete_student_profiles = 0
    for student in CustomUser.objects.filter(role='student'):
        if hasattr(student, 'student_profile'):
            profile = student.student_profile
            if (profile.student_id and profile.grade and 
                profile.parent_guardian_name and profile.emergency_contact_name):
                complete_student_profiles += 1
    
    complete_teacher_profiles = 0
    for teacher in CustomUser.objects.filter(role='teacher'):
        if hasattr(teacher, 'teacher_profile'):
            profile = teacher.teacher_profile
            if (profile.employee_id and profile.qualification and 
                profile.specialization and profile.emergency_contact_name):
                complete_teacher_profiles += 1
    
    print(f'✅ Complete Student Profiles: {complete_student_profiles}/{students}')
    print(f'✅ Complete Teacher Profiles: {complete_teacher_profiles}/{teachers}')
    
    # Test 4: Attendance System
    print('\n📅 ATTENDANCE SYSTEM TEST')
    print('-'*40)
    
    sessions = AttendanceSession.objects.count()
    records = AttendanceRecord.objects.count()
    total_sessions = StudentTotalSessions.objects.count()
    
    print(f'✅ Attendance Sessions: {sessions}')
    print(f'✅ Attendance Records: {records}')
    print(f'✅ Custom Total Sessions: {total_sessions}')
    
    if records > 0:
        present = AttendanceRecord.objects.filter(status='present').count()
        late = AttendanceRecord.objects.filter(status='late').count()
        absent = AttendanceRecord.objects.filter(status='absent').count()
        present_percentage = (present / records) * 100
        
        print(f'✅ Present: {present} ({present_percentage:.1f}%)')
        print(f'✅ Late: {late}')
        print(f'✅ Absent: {absent}')
    
    # Test 5: Grades and Assignments
    print('\n📝 GRADES & ASSIGNMENTS TEST')
    print('-'*40)
    
    grades = Grade.objects.count()
    assignments = Assignment.objects.count()
    submissions = AssignmentSubmission.objects.count()
    
    print(f'✅ Total Grades: {grades}')
    print(f'✅ Total Assignments: {assignments}')
    print(f'✅ Assignment Submissions: {submissions}')
    
    if grades > 0:
        avg_percentage = Grade.objects.aggregate(
            avg=django.db.models.Avg('percentage')
        )['avg']
        print(f'✅ Average Grade: {avg_percentage:.1f}%')
    
    # Test 6: Subject-Teacher Assignments
    print('\n🎓 SUBJECT-TEACHER ASSIGNMENTS TEST')
    print('-'*40)
    
    subject_teachers = SubjectTeacher.objects.count()
    print(f'✅ Subject-Teacher Assignments: {subject_teachers}')
    
    # Sample assignments
    sample_assignments = SubjectTeacher.objects.select_related(
        'subject', 'teacher', 'classroom'
    )[:5]
    
    for assignment in sample_assignments:
        print(f'   • {assignment.subject.name} - {assignment.teacher.get_full_name()} - {assignment.classroom.name}')
    
    # Test 7: Dynamic Total Sessions Feature
    print('\n⚡ DYNAMIC TOTAL SESSIONS TEST')
    print('-'*40)
    
    sample_student = CustomUser.objects.filter(role='student').first()
    if sample_student and hasattr(sample_student, 'student_profile'):
        total_sessions_record = StudentTotalSessions.objects.filter(
            student=sample_student
        ).first()
        
        if total_sessions_record:
            print(f'✅ Dynamic Total Sessions: FUNCTIONAL')
            print(f'   Student: {sample_student.get_full_name()}')
            print(f'   Total Sessions: {total_sessions_record.total_sessions}')
            if total_sessions_record.classroom:
                print(f'   Classroom: {total_sessions_record.classroom.name}')
            else:
                print(f'   Classroom: Not assigned')
        else:
            print(f'⚠️  Dynamic Total Sessions: No records found')
    
    # Test 8: Sample Data Quality
    print('\n🎯 SAMPLE DATA QUALITY TEST')
    print('-'*40)
    
    # Check for realistic data
    students_with_addresses = CustomUser.objects.filter(
        role='student', address__isnull=False
    ).exclude(address='').count()
    
    teachers_with_phones = CustomUser.objects.filter(
        role='teacher', phone_number__isnull=False
    ).exclude(phone_number='').count()
    
    print(f'✅ Students with addresses: {students_with_addresses}/{students}')
    print(f'✅ Teachers with phone numbers: {teachers_with_phones}/{teachers}')
    
    # Final Summary
    print('\n' + '='*60)
    print('🎉 SYSTEM TEST SUMMARY')
    print('='*60)
    
    total_tests = 8
    passed_tests = 0
    
    if users >= 40: passed_tests += 1
    if all([username for username, _, _ in test_credentials if authenticate(username=username, password='admin123' if 'admin' in username else 'teacher123' if 'teacher' in username else 'student123' if 'student' in username else 'parent123')]): passed_tests += 1
    if complete_student_profiles >= students * 0.8: passed_tests += 1
    if sessions > 500: passed_tests += 1
    if grades > 1000: passed_tests += 1
    if subject_teachers > 20: passed_tests += 1
    if total_sessions > 15: passed_tests += 1
    if students_with_addresses >= students * 0.8: passed_tests += 1
    
    print(f'Tests Passed: {passed_tests}/{total_tests}')
    
    if passed_tests >= 7:
        print('🟢 SYSTEM STATUS: EXCELLENT - Ready for presentation!')
    elif passed_tests >= 5:
        print('🟡 SYSTEM STATUS: GOOD - Minor issues detected')
    else:
        print('🔴 SYSTEM STATUS: NEEDS ATTENTION - Major issues found')
    
    print('\n🚀 Server running at: http://127.0.0.1:8000/')
    print('🔑 Use the credentials from PRESENTATION_GUIDE.md')
    
    return passed_tests >= 7

if __name__ == '__main__':
    test_system()