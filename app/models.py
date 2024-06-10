from django.db import models

class Number(models.Model):
    prefix = models.CharField(max_length=10)
    number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
