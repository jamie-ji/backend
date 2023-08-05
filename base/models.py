from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=500000, blank=True)
    # file = models.FileField(upload_to='documents/', blank=True)

    def __str__(self):
        return self.body[:50]
