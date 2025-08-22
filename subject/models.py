from django.db import models
from django.conf import settings
from classroom.models import Classroom
import uuid

class Subject(models.Model):
    subject_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.subject_id:
            # Generate unique subject ID
            import random
            self.subject_id = f"SUB{random.randint(10000000, 99999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.subject_id})"

class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_teachers')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subject_teachers')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='subject_teachers')

    def __str__(self):
        return f"{self.subject.name} - {self.teacher.username} - {self.classroom.name}"
