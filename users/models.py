from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        blank=True, 
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    permissions_level = models.CharField(
        max_length=20,
        choices=[
            ('super_admin', 'Super Admin'),
            ('admin', 'Admin'),
            ('moderator', 'Moderator'),
        ],
        default='admin'
    )
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"ADM{str(uuid.uuid4().int)[:8]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Admin: {self.user.get_full_name()}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(max_length=20, unique=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=200, blank=True)
    hire_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.teacher_id:
            # Generate 4-digit ID with first two letters from name
            first_initial = self.user.first_name[:2].upper() if self.user.first_name else 'TC'
            import random
            number = random.randint(10, 99)
            self.teacher_id = f"{first_initial}{number:02d}"
        if not self.employee_id:
            # Generate employee ID
            first_initial = self.user.first_name[:2].upper() if self.user.first_name else 'EM'
            import random
            number = random.randint(10, 99)
            self.employee_id = f"{first_initial}{number:02d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Teacher: {self.user.get_full_name()} ({self.teacher_id})"

class StudentProfile(models.Model):
    GRADE_CHOICES = [
        ('kindergarten', 'Kindergarten'),
        ('1st', '1st Grade'),
        ('2nd', '2nd Grade'),
        ('3rd', '3rd Grade'),
        ('4th', '4th Grade'),
        ('5th', '5th Grade'),
        ('6th', '6th Grade'),
        ('7th', '7th Grade'),
        ('8th', '8th Grade'),
        ('9th', '9th Grade'),
        ('10th', '10th Grade'),
        ('11th', '11th Grade'),
        ('12th', '12th Grade'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    roll_number = models.CharField(max_length=20, blank=True)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, blank=True)
    classroom = models.ForeignKey('classroom.Classroom', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    admission_date = models.DateField(blank=True, null=True)
    parent_guardian_name = models.CharField(max_length=100, blank=True)
    parent_guardian_phone = models.CharField(max_length=15, blank=True)
    parent_guardian_email = models.EmailField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    medical_conditions = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate 4-digit ID with first two letters from name
            first_initial = self.user.first_name[:2].upper() if self.user.first_name else 'ST'
            import random
            number = random.randint(10, 99)
            self.student_id = f"{first_initial}{number:02d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Student: {self.user.get_full_name()} ({self.student_id})"

class ParentProfile(models.Model):
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent_profile')
    students = models.ManyToManyField(StudentProfile, related_name='parents', blank=True)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='parent')
    occupation = models.CharField(max_length=100, blank=True)
    workplace = models.CharField(max_length=200, blank=True)
    work_phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Parent: {self.user.get_full_name()} ({self.get_relationship_display()})"
    
    def get_children(self):
        return self.students.all()

# Signal to create profiles automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'admin':
            AdminProfile.objects.create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.create(user=instance)
        elif instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'parent':
            ParentProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'admin' and hasattr(instance, 'admin_profile'):
        instance.admin_profile.save()
    elif instance.role == 'teacher' and hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
    elif instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'parent' and hasattr(instance, 'parent_profile'):
        instance.parent_profile.save()
