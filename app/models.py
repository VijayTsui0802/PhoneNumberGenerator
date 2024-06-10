from django.db import models

class Number(models.Model):
    prefix = models.CharField(max_length=10)
    number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')
    progress = models.FloatField(default=0)
    result = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
