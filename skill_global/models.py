from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    message = models.TextField(blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or (self.username or '')


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return getattr(self.user, 'get_full_name', lambda: str(self.user))() or str(self.user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # create a profile if one doesn't exist; keep safe for migrating users
        Profile.objects.get_or_create(user=instance)


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
    PROGRAMMING = 'Programming'
    DATA_SCIENCE = 'Data Science'
    AI = 'Artificial Intelligence'
    DIGITAL_MARKETING = 'Digital Marketing'
    LEADERSHIP = 'Leadership'
    UI_UX = 'UI/UX Design'

    MEETING_GOOGLE = 'Google Meet'
    MEETING_ZOOM = 'Zoom'
    MEETING_TEAMS = 'Microsoft Teams'

    SESSION_LIVE = 'Live Session'
    SESSION_WEBINAR = 'Webinar'
    SESSION_WORKSHOP = 'Workshop'
    SESSION_MASTERCLASS = 'Masterclass'

    LEVEL_BEGINNER = 'Beginner'
    LEVEL_INTERMEDIATE = 'Intermediate'
    LEVEL_ADVANCED = 'Advanced'

    STATUS_UPCOMING = 'Upcoming'
    STATUS_LIVE = 'Live Now'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    CATEGORY_CHOICES = [
        (PROGRAMMING, PROGRAMMING),
        (DATA_SCIENCE, DATA_SCIENCE),
        (AI, AI),
        (DIGITAL_MARKETING, DIGITAL_MARKETING),
        (LEADERSHIP, LEADERSHIP),
        (UI_UX, UI_UX),
    ]

    MEETING_PLATFORM_CHOICES = [
        (MEETING_GOOGLE, MEETING_GOOGLE),
        (MEETING_ZOOM, MEETING_ZOOM),
        (MEETING_TEAMS, MEETING_TEAMS),
    ]

    CLASS_TYPE_CHOICES = [
        (SESSION_LIVE, SESSION_LIVE),
        (SESSION_WEBINAR, SESSION_WEBINAR),
        (SESSION_WORKSHOP, SESSION_WORKSHOP),
        (SESSION_MASTERCLASS, SESSION_MASTERCLASS),
    ]

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, LEVEL_BEGINNER),
        (LEVEL_INTERMEDIATE, LEVEL_INTERMEDIATE),
        (LEVEL_ADVANCED, LEVEL_ADVANCED),
    ]

    STATUS_CHOICES = [
        (STATUS_UPCOMING, STATUS_UPCOMING),
        (STATUS_LIVE, STATUS_LIVE),
        (STATUS_COMPLETED, STATUS_COMPLETED),
        (STATUS_CANCELLED, STATUS_CANCELLED),
    ]

    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=150, blank=True)
    topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=120, choices=CATEGORY_CHOICES, blank=True)
    thumbnail = models.ImageField(upload_to='liveclasses/thumbnails/', blank=True, null=True)
    meeting_platform = models.CharField(max_length=50, choices=MEETING_PLATFORM_CHOICES, blank=True)
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=100, blank=True)
    class_type = models.CharField(max_length=50, choices=CLASS_TYPE_CHOICES, blank=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True)
    language = models.CharField(max_length=80, blank=True)
    max_students = models.PositiveIntegerField(default=0)
    enrolled_students = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    certificate_available = models.BooleanField(default=False)
    recording_available = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    duration = models.CharField(max_length=80, blank=True)
    prerequisites = models.TextField(blank=True)
    learning_outcomes = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    banner_color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Live Class'
        verbose_name_plural = 'Live Classes'
        ordering = ['display_order', 'scheduled_at']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    student_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-id']

    def __str__(self):
        return self.student_name


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.CharField(max_length=100, blank=True)
    author = models.CharField(max_length=150, blank=True)

    summary = models.CharField(max_length=255, blank=True)
    content = models.TextField()

    image = models.ImageField(upload_to='articles/', blank=True, null=True)

    read_time = models.PositiveIntegerField(default=5)
    tags = models.CharField(max_length=255, blank=True)

    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title