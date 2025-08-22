from django.db import models
from django.contrib.auth import get_user_model
from subject.models import Subject
from classroom.models import Classroom

User = get_user_model()

class Grade(models.Model):
    GRADE_TYPES = [
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('project', 'Project'),
        ('participation', 'Participation'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_grades')
    
    title = models.CharField(max_length=200)
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPES)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2)
    points_possible = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    
    date_assigned = models.DateField()
    date_due = models.DateField(null=True, blank=True)
    date_graded = models.DateTimeField(auto_now_add=True)
    
    comments = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if self.points_possible > 0:
            self.percentage = (self.points_earned / self.points_possible) * 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title} ({self.percentage}%)"
    
    class Meta:
        ordering = ['-date_graded']