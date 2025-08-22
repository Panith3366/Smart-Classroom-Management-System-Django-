from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, StudentProfile, TeacherProfile, AdminProfile, ParentProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create appropriate profile when a user is created"""
    if created:
        if instance.role == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.get_or_create(user=instance)
        elif instance.role == 'admin':
            AdminProfile.objects.get_or_create(user=instance)
        elif instance.role == 'parent':
            ParentProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when user is saved"""
    try:
        if instance.role == 'student' and hasattr(instance, 'student_profile'):
            instance.student_profile.save()
        elif instance.role == 'teacher' and hasattr(instance, 'teacher_profile'):
            instance.teacher_profile.save()
        elif instance.role == 'admin' and hasattr(instance, 'admin_profile'):
            instance.admin_profile.save()
        elif instance.role == 'parent' and hasattr(instance, 'parent_profile'):
            instance.parent_profile.save()
    except Exception:
        # If profile doesn't exist, create it
        if instance.role == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.get_or_create(user=instance)
        elif instance.role == 'admin':
            AdminProfile.objects.get_or_create(user=instance)
        elif instance.role == 'parent':
            ParentProfile.objects.get_or_create(user=instance)