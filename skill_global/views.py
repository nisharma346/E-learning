from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser, LiveClass, Article, Course, About

# Create your views here.

def index(request):
    courses = Course.objects.filter(is_active=True).order_by('title')[:3]
    about = About.objects.first()
    context = {
        'page_title': 'Home',
        'page_description': 'Skill Global offers premium training, live mentoring, and certification pathways for students and professionals ready to accelerate their career.',
        'courses': courses,
        'about': about,
    }
    return render(request, 'skill_global/index.html', context)


def courses(request):
    courses = Course.objects.filter(is_active=True).order_by('title')
    context = {
        'page_title': 'Courses',
        'page_description': 'Browse premium courses designed to help you build career-ready skills.',
        'courses': courses,
    }
    return render(request, 'skill_global/courses.html', context)


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
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        if not full_name or not email or not phone or not password:
            context['error'] = 'Please fill in all fields.'
        elif CustomUser.objects.filter(email=email).exists():
            context['error'] = 'A user with that email already exists.'
        else:
            hashed_password = make_password(password)
            CustomUser.objects.create(
                name=full_name,
                email=email,
                phone=phone,
                password=hashed_password,
            )
            context['success'] = 'Registration successful. You can now log in.'

    return render(request, 'skill_global/register.html', context)


def profile(request):
    user = request.user
    context = {
        'page_title': 'Profile',
        'page_description': 'View your account details and learning progress.',
        'user': user,
    }
    return render(request, 'skill_global/profile.html', context)


def about(request):
    about = About.objects.first()
    context = {
        'page_title': 'About Us',
        'page_description': 'Learn. Practice. Grow. Build an industry-ready career with Skill Global.',
        'about': about,
    }
    return render(request, 'skill_global/about.html', context)
