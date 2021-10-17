from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

# Create your models here.
class Notification_Id(models.Model):
    key = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.key

class Analytics_event(models.Model):
    name = models.CharField(max_length=150)
    time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Notification(models.Model):
    title = models.CharField(max_length=120)
    time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
