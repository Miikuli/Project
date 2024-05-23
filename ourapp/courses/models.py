from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    files = models.ManyToManyField('File', related_name='courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    # users = models.ManyToManyField(User, related_name='courses', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses', default=1)
    subscribers = models.ManyToManyField(User, related_name='subscribed_courses', blank=True)

class File(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='courses_files/', null=True, blank=True)