from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('courses/', views.courses, name='courses'),
    path('articles/', views.articles, name='articles'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contact/', views.contact, name='contact'),
    path('live-classes/', views.live_classes, name='live_classes'),
    path('register/', views.register, name='register'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('about/', views.about, name='about'),
]
