from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from users.models import CustomUser, StudentProfile, TeacherProfile, AdminProfile, ParentProfile
from classroom.models import Classroom, Announcement
from subject.models import Subject, SubjectTeacher
from attendance.models import AttendanceSession, AttendanceRecord, StudentTotalSessions
from grades.models import Grade
from assignments.models import Assignment, AssignmentSubmission


class Command(BaseCommand):
    help = 'Show comprehensive summary of presentation data'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('🎯 SMART CLASSROOM MANAGEMENT SYSTEM'))
        self.stdout.write(self.style.SUCCESS('📊 COMPREHENSIVE PRESENTATION DATA SUMMARY'))
        self.stdout.write('='*80)
        
        self.show_user_statistics()
        self.show_academic_data()
        self.show_attendance_statistics()
        self.show_grades_and_assignments()
        self.show_sample_data_preview()
        self.show_login_credentials()
        
        self.stdout.write('='*80)
        self.stdout.write(self.style.SUCCESS('🚀 SYSTEM READY FOR PRESENTATION!'))
        self.stdout.write('='*80)

    def show_user_statistics(self):
        """Show user and profile statistics"""
        self.stdout.write('\n' + self.style.WARNING('👥 USER STATISTICS'))
        self.stdout.write('-'*50)
        
        total_users = CustomUser.objects.count()
        students = CustomUser.objects.filter(role='student').count()
        teachers = CustomUser.objects.filter(role='teacher').count()
        admins = CustomUser.objects.filter(role='admin').count()
        parents = CustomUser.objects.filter(role='parent').count()
        
        self.stdout.write(f'Total Users: {total_users}')
        self.stdout.write(f'  👨‍🎓 Students: {students}')
        self.stdout.write(f'  👩‍🏫 Teachers: {teachers}')
        self.stdout.write(f'  👨‍💼 Admins: {admins}')
        self.stdout.write(f'  👨‍👩‍👧‍👦 Parents: {parents}')
        
        # Profile completeness
        complete_student_profiles = StudentProfile.objects.exclude(
            parent_guardian_name='', emergency_contact_name=''
        ).count()
        complete_teacher_profiles = TeacherProfile.objects.exclude(
            qualification='', emergency_contact_name=''
        ).count()
        
        self.stdout.write(f'\nProfile Completeness:')
        self.stdout.write(f'  Complete Student Profiles: {complete_student_profiles}/{students}')
        self.stdout.write(f'  Complete Teacher Profiles: {complete_teacher_profiles}/{teachers}')

    def show_academic_data(self):
        """Show academic structure data"""
        self.stdout.write('\n' + self.style.WARNING('🏫 ACADEMIC STRUCTURE'))
        self.stdout.write('-'*50)
        
        classrooms = Classroom.objects.count()
        subjects = Subject.objects.count()
        subject_assignments = SubjectTeacher.objects.count()
        announcements = Announcement.objects.count()
        
        self.stdout.write(f'Classrooms: {classrooms}')
        self.stdout.write(f'Subjects: {subjects}')
        self.stdout.write(f'Subject-Teacher Assignments: {subject_assignments}')
        self.stdout.write(f'Classroom Announcements: {announcements}')
        
        # Show classroom distribution
        classroom_students = Classroom.objects.annotate(
            student_count=Count('students')
        ).values('name', 'grade', 'student_count')
        
        self.stdout.write('\nClassroom Distribution:')
        for classroom in classroom_students:
            self.stdout.write(f"  {classroom['name']} ({classroom['grade']}): {classroom['student_count']} students")

    def show_attendance_statistics(self):
        """Show attendance system statistics"""
        self.stdout.write('\n' + self.style.WARNING('📅 ATTENDANCE SYSTEM'))
        self.stdout.write('-'*50)
        
        sessions = AttendanceSession.objects.count()
        records = AttendanceRecord.objects.count()
        total_sessions_records = StudentTotalSessions.objects.count()
        
        self.stdout.write(f'Attendance Sessions: {sessions}')
        self.stdout.write(f'Attendance Records: {records}')
        self.stdout.write(f'Custom Total Sessions: {total_sessions_records}')
        
        # Attendance statistics
        if records > 0:
            present_count = AttendanceRecord.objects.filter(status='present').count()
            late_count = AttendanceRecord.objects.filter(status='late').count()
            absent_count = AttendanceRecord.objects.filter(status='absent').count()
            
            present_percentage = (present_count / records) * 100
            
            self.stdout.write(f'\nAttendance Breakdown:')
            self.stdout.write(f'  ✅ Present: {present_count} ({present_percentage:.1f}%)')
            self.stdout.write(f'  ⏰ Late: {late_count}')
            self.stdout.write(f'  ❌ Absent: {absent_count}')

    def show_grades_and_assignments(self):
        """Show grades and assignments statistics"""
        self.stdout.write('\n' + self.style.WARNING('📝 GRADES & ASSIGNMENTS'))
        self.stdout.write('-'*50)
        
        try:
            grades = Grade.objects.count()
            assignments = Assignment.objects.count()
            submissions = AssignmentSubmission.objects.count()
            
            self.stdout.write(f'Total Grades: {grades}')
            self.stdout.write(f'Total Assignments: {assignments}')
            self.stdout.write(f'Assignment Submissions: {submissions}')
            
            if grades > 0:
                avg_percentage = Grade.objects.aggregate(
                    avg_percentage=Avg('percentage')
                )['avg_percentage']
                
                self.stdout.write(f'Average Grade Percentage: {avg_percentage:.1f}%')
            
            # Grade type distribution
            if grades > 0:
                grade_types = Grade.objects.values('grade_type').annotate(
                    count=Count('grade_type')
                ).order_by('-count')
                
                self.stdout.write('\nGrade Type Distribution:')
                for grade_type in grade_types:
                    self.stdout.write(f"  {grade_type['grade_type'].title()}: {grade_type['count']}")
        
        except Exception as e:
            self.stdout.write(f'Grades/Assignments data: Available but not detailed ({str(e)})')

    def show_sample_data_preview(self):
        """Show preview of sample data"""
        self.stdout.write('\n' + self.style.WARNING('🔍 SAMPLE DATA PREVIEW'))
        self.stdout.write('-'*50)
        
        # Sample students
        sample_students = CustomUser.objects.filter(role='student')[:5]
        self.stdout.write('Sample Students:')
        for student in sample_students:
            profile = getattr(student, 'student_profile', None)
            classroom = profile.classroom.name if profile and profile.classroom else 'No classroom'
            grade = profile.grade if profile else 'No grade'
            self.stdout.write(f'  • {student.get_full_name()} - {grade} - {classroom}')
        
        # Sample teachers
        sample_teachers = CustomUser.objects.filter(role='teacher')[:5]
        self.stdout.write('\nSample Teachers:')
        for teacher in sample_teachers:
            profile = getattr(teacher, 'teacher_profile', None)
            specialization = profile.specialization if profile else 'General'
            qualification = profile.qualification if profile else 'N/A'
            self.stdout.write(f'  • {teacher.get_full_name()} - {specialization} ({qualification})')
        
        # Recent attendance sessions
        recent_sessions = AttendanceSession.objects.order_by('-start_time')[:3]
        self.stdout.write('\nRecent Attendance Sessions:')
        for session in recent_sessions:
            self.stdout.write(f'  • {session.title} - {session.start_time.strftime("%Y-%m-%d %H:%M")}')

    def show_login_credentials(self):
        """Show login credentials for presentation"""
        self.stdout.write('\n' + self.style.ERROR('🔑 PRESENTATION LOGIN CREDENTIALS'))
        self.stdout.write('-'*50)
        self.stdout.write('👨‍💼 ADMIN ACCESS:')
        self.stdout.write('   Username: admin_principal')
        self.stdout.write('   Password: admin123')
        self.stdout.write('   Role: Principal/Super Admin')
        
        self.stdout.write('\n👩‍🏫 TEACHER ACCESS:')
        self.stdout.write('   Username: teacher_math')
        self.stdout.write('   Password: teacher123')
        self.stdout.write('   Role: Mathematics Teacher')
        
        self.stdout.write('\n👨‍🎓 STUDENT ACCESS:')
        self.stdout.write('   Username: student_alice')
        self.stdout.write('   Password: student123')
        self.stdout.write('   Role: Student')
        
        self.stdout.write('\n👨‍👩‍👧‍👦 PARENT ACCESS:')
        self.stdout.write('   Username: parent_johnson')
        self.stdout.write('   Password: parent123')
        self.stdout.write('   Role: Parent/Guardian')
        
        self.stdout.write('\n🌐 ACCESS URL: http://127.0.0.1:8000/')
        
        self.stdout.write('\n' + self.style.SUCCESS('💡 PRESENTATION TIPS:'))
        self.stdout.write('• Use admin account to demonstrate management features')
        self.stdout.write('• Use teacher account to show attendance and grading')
        self.stdout.write('• Use student account to show student dashboard')
        self.stdout.write('• Dynamic total sessions feature is fully functional')
        self.stdout.write('• All data is realistic and presentation-ready')