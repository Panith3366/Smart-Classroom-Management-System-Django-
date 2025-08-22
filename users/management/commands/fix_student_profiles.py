from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser, StudentProfile, TeacherProfile, AdminProfile, ParentProfile


class Command(BaseCommand):
    help = 'Create missing profiles for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating profiles',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Fix student profiles
        students_without_profile = CustomUser.objects.filter(
            role='student'
        ).exclude(
            id__in=StudentProfile.objects.values_list('user_id', flat=True)
        )
        
        # Fix teacher profiles
        teachers_without_profile = CustomUser.objects.filter(
            role='teacher'
        ).exclude(
            id__in=TeacherProfile.objects.values_list('user_id', flat=True)
        )
        
        # Fix admin profiles
        admins_without_profile = CustomUser.objects.filter(
            role='admin'
        ).exclude(
            id__in=AdminProfile.objects.values_list('user_id', flat=True)
        )
        
        # Fix parent profiles
        parents_without_profile = CustomUser.objects.filter(
            role='parent'
        ).exclude(
            id__in=ParentProfile.objects.values_list('user_id', flat=True)
        )
        
        total_fixes = (
            students_without_profile.count() + 
            teachers_without_profile.count() + 
            admins_without_profile.count() + 
            parents_without_profile.count()
        )
        
        if total_fixes == 0:
            self.stdout.write(self.style.SUCCESS('All users already have profiles!'))
            return
        
        self.stdout.write(f'Found {total_fixes} users without profiles:')
        self.stdout.write(f'  - Students: {students_without_profile.count()}')
        self.stdout.write(f'  - Teachers: {teachers_without_profile.count()}')
        self.stdout.write(f'  - Admins: {admins_without_profile.count()}')
        self.stdout.write(f'  - Parents: {parents_without_profile.count()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Run without --dry-run to create these profiles'))
            return
        
        created_count = 0
        
        with transaction.atomic():
            # Create student profiles
            for student in students_without_profile:
                StudentProfile.objects.create(user=student)
                created_count += 1
                self.stdout.write(f'Created student profile for: {student.get_full_name()}')
            
            # Create teacher profiles
            for teacher in teachers_without_profile:
                TeacherProfile.objects.create(user=teacher)
                created_count += 1
                self.stdout.write(f'Created teacher profile for: {teacher.get_full_name()}')
            
            # Create admin profiles
            for admin in admins_without_profile:
                AdminProfile.objects.create(user=admin)
                created_count += 1
                self.stdout.write(f'Created admin profile for: {admin.get_full_name()}')
            
            # Create parent profiles
            for parent in parents_without_profile:
                ParentProfile.objects.create(user=parent)
                created_count += 1
                self.stdout.write(f'Created parent profile for: {parent.get_full_name()}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} profiles!')
        )