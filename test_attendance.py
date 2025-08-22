#!/usr/bin/env python
"""
Quick test script to verify attendance system functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')
django.setup()

from users.models import CustomUser, StudentProfile
from attendance.models import StudentTotalSessions

def test_student_profiles():
    print("=== Testing Student Profiles ===")
    
    students = CustomUser.objects.filter(role='student')
    print(f"Total students: {students.count()}")
    
    students_with_profiles = 0
    students_without_profiles = 0
    
    for student in students:
        if hasattr(student, 'student_profile') and student.student_profile:
            students_with_profiles += 1
            print(f"✅ {student.get_full_name()} - Has profile (ID: {student.student_profile.student_id})")
        else:
            students_without_profiles += 1
            print(f"❌ {student.get_full_name()} - Missing profile")
    
    print(f"\nSummary:")
    print(f"  Students with profiles: {students_with_profiles}")
    print(f"  Students without profiles: {students_without_profiles}")
    
    return students_without_profiles == 0

def test_total_sessions():
    print("\n=== Testing Total Sessions ===")
    
    total_sessions_records = StudentTotalSessions.objects.all()
    print(f"Custom total sessions records: {total_sessions_records.count()}")
    
    for record in total_sessions_records:
        print(f"📊 {record.student.get_full_name()}: {record.total_sessions} sessions")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Attendance System\n")
    
    profiles_ok = test_student_profiles()
    sessions_ok = test_total_sessions()
    
    print(f"\n{'='*50}")
    if profiles_ok and sessions_ok:
        print("✅ All tests passed! Attendance system is ready.")
    else:
        print("❌ Some issues found. Please check the output above.")
    print(f"{'='*50}")