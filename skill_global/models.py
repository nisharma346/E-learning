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


class About(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About'
        verbose_name_plural = 'About Entries'

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=150, blank=True)
    duration = models.CharField(max_length=80, blank=True)
    level = models.CharField(max_length=80, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['title']

    def __str__(self):
        return self.title


class LiveClass(models.Model):
    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=150, blank=True)
    topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    duration = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Live Class'
        verbose_name_plural = 'Live Classes'
        ordering = ['scheduled_at']

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150, blank=True)
    summary = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title
