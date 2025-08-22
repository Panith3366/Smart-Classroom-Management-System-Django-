from django.db import models
from django.conf import settings
from classroom.models import Classroom
from subject.models import Subject

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='old_teacher_profile')

    def __str__(self):
        return self.user.username

class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    file = models.FileField(upload_to='assignments/')
    due_date = models.DateField()

    def __str__(self):
        return f"Assignment for {self.classroom.name} - {self.subject.name}"

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quizzes')
    questions = models.JSONField()

    def __str__(self):
        return self.title
