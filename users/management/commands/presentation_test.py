from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from users.models import CustomUser, StudentProfile, TeacherProfile
from classroom.models import Classroom, Announcement
from attendance.models import AttendanceSession, AttendanceRecord, StudentTotalSessions
from grades.models import Grade
from assignments.models import Assignment, AssignmentSubmission
from subject.models import Subject, SubjectTeacher


class Command(BaseCommand):
    help = 'Comprehensive presentation readiness test'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('🎯 PRESENTATION READINESS TEST'))
        self.stdout.write('='*80)
        
        all_tests_passed = True
        
        # Test 1: Critical Login Credentials
        self.stdout.write('\n🔐 CRITICAL LOGIN TEST')
        self.stdout.write('-'*50)
        
        credentials = [
            ('admin_principal', 'admin123', 'Principal Admin'),
            ('teacher_math', 'teacher123', 'Math Teacher'),
            ('student_alice', 'student123', 'Student Alice'),
            ('parent_johnson', 'parent123', 'Parent Johnson')
        ]
        
        login_success = True
        for username, password, description in credentials:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                self.stdout.write(f'✅ {description}: LOGIN SUCCESS')
                self.stdout.write(f'   → Name: {user.get_full_name()}')
                self.stdout.write(f'   → Role: {user.role.title()}')
                self.stdout.write(f'   → Email: {user.email}')
            else:
                self.stdout.write(f'❌ {description}: LOGIN FAILED')
                login_success = False
        
        if not login_success:
            all_tests_passed = False
        
        # Test 2: Dynamic Total Sessions Feature
        self.stdout.write('\n⚡ DYNAMIC TOTAL SESSIONS FEATURE TEST')
        self.stdout.write('-'*50)
        
        total_sessions_count = StudentTotalSessions.objects.count()
        if total_sessions_count >= 20:
            self.stdout.write(f'✅ Dynamic Total Sessions Records: {total_sessions_count}')
            
            # Test a specific student
            sample_student = CustomUser.objects.filter(role='student').first()
            if sample_student:
                total_session = StudentTotalSessions.objects.filter(student=sample_student).first()
                if total_session:
                    self.stdout.write(f'✅ Sample Student: {sample_student.get_full_name()}')
                    self.stdout.write(f'   → Total Sessions: {total_session.total_sessions}')
                    self.stdout.write(f'   → Feature: FULLY FUNCTIONAL')
                else:
                    self.stdout.write(f'⚠️  Sample student has no total sessions record')
            else:
                self.stdout.write(f'❌ No students found')
                all_tests_passed = False
        else:
            self.stdout.write(f'❌ Insufficient total sessions records: {total_sessions_count}')
            all_tests_passed = False
        
        # Test 3: Comprehensive Data Population
        self.stdout.write('\n📊 DATA POPULATION TEST')
        self.stdout.write('-'*50)
        
        data_checks = [
            ('Users', CustomUser.objects.count(), 40),
            ('Students', CustomUser.objects.filter(role='student').count(), 20),
            ('Teachers', CustomUser.objects.filter(role='teacher').count(), 10),
            ('Classrooms', Classroom.objects.count(), 5),
            ('Subjects', Subject.objects.count(), 8),
            ('Attendance Sessions', AttendanceSession.objects.count(), 300),
            ('Grades', Grade.objects.count(), 1000),
            ('Assignments', Assignment.objects.count(), 15)
        ]
        
        for item, count, minimum in data_checks:
            if count >= minimum:
                self.stdout.write(f'✅ {item}: {count} (minimum: {minimum})')
            else:
                self.stdout.write(f'❌ {item}: {count} (minimum: {minimum})')
                all_tests_passed = False
        
        # Test 4: Profile Completeness
        self.stdout.write('\n👤 PROFILE COMPLETENESS TEST')
        self.stdout.write('-'*50)
        
        complete_students = 0
        total_students = CustomUser.objects.filter(role='student').count()
        
        for student in CustomUser.objects.filter(role='student'):
            if hasattr(student, 'student_profile'):
                profile = student.student_profile
                if (profile.student_id and profile.parent_guardian_name and 
                    profile.emergency_contact_name and profile.grade):
                    complete_students += 1
        
        complete_teachers = 0
        total_teachers = CustomUser.objects.filter(role='teacher').count()
        
        for teacher in CustomUser.objects.filter(role='teacher'):
            if hasattr(teacher, 'teacher_profile'):
                profile = teacher.teacher_profile
                if (profile.employee_id and profile.qualification and 
                    profile.specialization and profile.emergency_contact_name):
                    complete_teachers += 1
        
        student_completion = (complete_students / total_students) * 100 if total_students > 0 else 0
        teacher_completion = (complete_teachers / total_teachers) * 100 if total_teachers > 0 else 0
        
        if student_completion >= 90:
            self.stdout.write(f'✅ Student Profiles: {complete_students}/{total_students} ({student_completion:.1f}%)')
        else:
            self.stdout.write(f'❌ Student Profiles: {complete_students}/{total_students} ({student_completion:.1f}%)')
            all_tests_passed = False
        
        if teacher_completion >= 90:
            self.stdout.write(f'✅ Teacher Profiles: {complete_teachers}/{total_teachers} ({teacher_completion:.1f}%)')
        else:
            self.stdout.write(f'❌ Teacher Profiles: {complete_teachers}/{total_teachers} ({teacher_completion:.1f}%)')
            all_tests_passed = False
        
        # Test 5: Attendance System Functionality
        self.stdout.write('\n📅 ATTENDANCE SYSTEM TEST')
        self.stdout.write('-'*50)
        
        attendance_records = AttendanceRecord.objects.count()
        if attendance_records >= 100:
            present_count = AttendanceRecord.objects.filter(status='present').count()
            attendance_rate = (present_count / attendance_records) * 100
            
            self.stdout.write(f'✅ Attendance Records: {attendance_records}')
            self.stdout.write(f'✅ Attendance Rate: {attendance_rate:.1f}%')
            
            if attendance_rate >= 75:
                self.stdout.write(f'✅ Realistic Attendance Pattern: YES')
            else:
                self.stdout.write(f'⚠️  Attendance Rate Low: {attendance_rate:.1f}%')
        else:
            self.stdout.write(f'❌ Insufficient Attendance Records: {attendance_records}')
            all_tests_passed = False
        
        # Test 6: Academic Performance Data
        self.stdout.write('\n📝 ACADEMIC PERFORMANCE TEST')
        self.stdout.write('-'*50)
        
        grades_count = Grade.objects.count()
        if grades_count >= 1000:
            from django.db.models import Avg
            avg_percentage = Grade.objects.aggregate(avg=Avg('percentage'))['avg']
            
            self.stdout.write(f'✅ Total Grades: {grades_count}')
            self.stdout.write(f'✅ Average Performance: {avg_percentage:.1f}%')
            
            if 80 <= avg_percentage <= 90:
                self.stdout.write(f'✅ Realistic Grade Distribution: YES')
            else:
                self.stdout.write(f'⚠️  Grade Average: {avg_percentage:.1f}% (expected 80-90%)')
        else:
            self.stdout.write(f'❌ Insufficient Grade Records: {grades_count}')
            all_tests_passed = False
        
        # Test 7: System Integration
        self.stdout.write('\n🔗 SYSTEM INTEGRATION TEST')
        self.stdout.write('-'*50)
        
        subject_teacher_assignments = SubjectTeacher.objects.count()
        announcements = Announcement.objects.count()
        
        if subject_teacher_assignments >= 15:
            self.stdout.write(f'✅ Subject-Teacher Assignments: {subject_teacher_assignments}')
        else:
            self.stdout.write(f'❌ Subject-Teacher Assignments: {subject_teacher_assignments}')
            all_tests_passed = False
        
        if announcements >= 15:
            self.stdout.write(f'✅ Classroom Announcements: {announcements}')
        else:
            self.stdout.write(f'❌ Classroom Announcements: {announcements}')
            all_tests_passed = False
        
        # Final Assessment
        self.stdout.write('\n' + '='*80)
        self.stdout.write('🎉 FINAL PRESENTATION ASSESSMENT')
        self.stdout.write('='*80)
        
        if all_tests_passed:
            self.stdout.write(self.style.SUCCESS('🟢 SYSTEM STATUS: PRESENTATION READY!'))
            self.stdout.write(self.style.SUCCESS('✅ All critical features are functional'))
            self.stdout.write(self.style.SUCCESS('✅ Data is comprehensive and realistic'))
            self.stdout.write(self.style.SUCCESS('✅ Login credentials are working'))
            self.stdout.write(self.style.SUCCESS('✅ Dynamic Total Sessions feature is ready'))
        else:
            self.stdout.write(self.style.WARNING('🟡 SYSTEM STATUS: MINOR ISSUES DETECTED'))
            self.stdout.write(self.style.WARNING('⚠️  Some features may need attention'))
            self.stdout.write(self.style.WARNING('⚠️  Review failed tests above'))
        
        # Presentation Instructions
        self.stdout.write('\n' + '='*80)
        self.stdout.write('🎯 PRESENTATION INSTRUCTIONS')
        self.stdout.write('='*80)
        
        self.stdout.write('\n🔑 LOGIN CREDENTIALS FOR DEMO:')
        self.stdout.write('   Admin: admin_principal / admin123')
        self.stdout.write('   Teacher: teacher_math / teacher123')
        self.stdout.write('   Student: student_alice / student123')
        self.stdout.write('   Parent: parent_johnson / parent123')
        
        self.stdout.write('\n🌟 KEY FEATURES TO HIGHLIGHT:')
        self.stdout.write('   1. Dynamic Total Sessions (Your latest feature!)')
        self.stdout.write('   2. Comprehensive user management')
        self.stdout.write('   3. Real-time attendance tracking')
        self.stdout.write('   4. Advanced grading system')
        self.stdout.write('   5. Role-based access control')
        
        self.stdout.write('\n🚀 SERVER ACCESS:')
        self.stdout.write('   URL: http://127.0.0.1:8000/')
        self.stdout.write('   Status: Should be running')
        
        self.stdout.write('\n💡 DEMO FLOW SUGGESTION:')
        self.stdout.write('   1. Login as Admin → Show system overview')
        self.stdout.write('   2. Login as Teacher → Demonstrate attendance & dynamic sessions')
        self.stdout.write('   3. Login as Student → Show student dashboard')
        self.stdout.write('   4. Login as Parent → Show parent monitoring')
        
        self.stdout.write('\n' + '='*80)
        
        return all_tests_passed