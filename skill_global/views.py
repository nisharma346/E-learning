from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CustomUser

# Create your views here.

def index(request):
    return render(request, 'skill_global/index.html')


def register(request):
    context = {}
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
def about(request):
    return render(request, 'about.html')
