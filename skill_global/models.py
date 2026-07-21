from django.db import models

# Create your models here.

class CustomUser(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.name
