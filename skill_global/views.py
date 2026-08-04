import math

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Profile, LiveClass, Article, Course, About, Testimonial

User = get_user_model()

# Create your views here.

def index(request):
    courses = Course.objects.filter(is_active=True).order_by('title')[:3]
    about = About.objects.first()
    live_classes = LiveClass.objects.filter(
        is_active=True,
        scheduled_at__gte=timezone.now()
    ).order_by('scheduled_at')[:3]
    latest_articles = list(Article.objects.filter(is_published=True).order_by('-published_at')[:3])
    for article in latest_articles:
        word_count = len(article.content.split()) if article.content else 0
        article.reading_time = max(1, math.ceil(word_count / 200))
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-id')[:3]
    context = {
        'page_title': 'Home',
        'page_description': 'Skill Global offers premium training, live mentoring, and certification pathways for students and professionals ready to accelerate their career.',
        'courses': courses,
        'about': about,
        'live_classes': live_classes,
        'latest_articles': latest_articles,
        'testimonials': testimonials,
    }
    return render(request, 'skill_global/index.html', context)


def testimonials(request):
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-id')
    context = {
        'page_title': 'Testimonials',
        'page_description': 'Read what learners are saying about Skill Global training and support.',
        'testimonials': testimonials,
    }
    return render(request, 'skill_global/testimonials.html', context)


def courses(request):
    courses = Course.objects.filter(is_active=True).order_by('title')
    context = {
        'page_title': 'Courses',
        'page_description': 'Browse premium courses designed to help you build career-ready skills.',
        'courses': courses,
    }
    return render(request, 'skill_global/courses.html', context)


def course_detail(request, id):
    course = Course.objects.filter(id=id, is_active=True).first()
    context = {
        'page_title': course.title if course else 'Course Details',
        'page_description': 'View detailed information about this course.',
        'course': course,
    }
    return render(request, 'skill_global/course_detail.html', context)


def live_classes(request):
    classes = LiveClass.objects.filter(is_active=True).order_by('scheduled_at')
    context = {
        'page_title': 'Live Classes',
        'page_description': 'Join live sessions led by experts and sharpen your skills in real time.',
        'classes': classes,
    }
    return render(request, 'skill_global/live_classes.html', context)


def articles(request):
    articles = Article.objects.filter(is_published=True).order_by('-published_at')
    context = {
        'page_title': 'Articles',
        'page_description': 'Read expert-written articles on career growth, industry skills, and learning best practices.',
        'articles': articles,
    }
    return render(request, 'skill_global/articles.html', context)


def contact(request):
    context = {
        'page_title': 'Contact',
        'page_description': 'Get in touch with Skill Global for questions about courses, partnerships, and learning support.',
    }
    return render(request, 'skill_global/contact.html', context)


def register(request):
    context = {
        'page_title': 'Register',
        'page_description': 'Create your account and start your learning journey with Skill Global.'
    }
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        if not full_name or not email or not password:
            context['error'] = 'Please fill in all fields.'
        elif User.objects.filter(email=email).exists():
            context['error'] = 'A user with that email already exists.'
        else:
            # create user via custom manager using email as identifier
            parts = full_name.split()
            first_name = parts[0] if parts else ''
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                phone=phone,
                message='',
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()
            auth_login(request, user)
            return redirect('profile')

    return render(request, 'skill_global/register.html', context)


def profile(request):
    user = request.user
    profile = None
    if user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=user)

    context = {
        'page_title': 'Profile',
        'page_description': 'View your account details and learning progress.',
        'user': user,
        'profile': profile,
        'stats': {
            'courses': Course.objects.filter(is_active=True).count(),
            'certificates': 5,
            'live_classes': LiveClass.objects.filter(is_active=True).count(),
            'articles': Article.objects.filter(is_published=True).count(),
        },
    }
    return render(request, 'skill_global/profile.html', context)


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('profile')

    context = {
        'page_title': 'Sign In',
        'page_description': 'Sign in to access your Skill Global account.'
    }

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        # authenticate using the model's USERNAME_FIELD (email)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Successfully signed in.')
            return redirect('profile')

        context['error'] = 'Invalid email or password.'

    return render(request, 'skill_global/login.html', context)


def sign_out(request):
    auth_logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home')


def edit_profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('profile')

    profile, _ = Profile.objects.get_or_create(user=user)
    errors = []

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()
        profile_image = request.FILES.get('profile_image')
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not full_name:
            errors.append('Full Name is required.')
        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors.append('Email is already in use.')

        if new_password or confirm_password:
            if new_password != confirm_password:
                errors.append('The new passwords do not match.')
            elif len(new_password) < 8:
                errors.append('Password must be at least 8 characters long.')

        if not errors:
            parts = full_name.split()
            user.first_name = parts[0] if parts else ''
            user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            user.full_name = full_name
            user.email = email
            if new_password and hasattr(user, 'set_password'):
                user.set_password(new_password)
            user.save()

            profile.phone = phone
            profile.bio = bio
            if profile_image:
                profile.image = profile_image
            profile.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

    context = {
        'page_title': 'Edit Profile',
        'page_description': 'Update your profile details.',
        'user': user,
        'profile': profile,
        'errors': errors,
    }
    return render(request, 'skill_global/edit_profile.html', context)


def about(request):
    about = About.objects.first()
    context = {
        'page_title': 'About Us',
        'page_description': 'Learn. Practice. Grow. Build an industry-ready career with Skill Global.',
        'about': about,
    }
    return render(request, 'skill_global/about.html', context)
