from django.db import models
from django.conf import settings
import uuid

class Classroom(models.Model):
    classroom_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classrooms')

    def save(self, *args, **kwargs):
        if not self.classroom_id:
            # Generate unique classroom ID
            import random
            self.classroom_id = f"CLS{random.randint(10000000, 99999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Grade {self.grade} ({self.classroom_id})"

class Announcement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement for {self.classroom.name} at {self.created_at}"
