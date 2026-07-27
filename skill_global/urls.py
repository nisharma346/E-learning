from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('courses/', views.courses, name='courses'),
    path('articles/', views.articles, name='articles'),
    path('contact/', views.contact, name='contact'),
    path('live-classes/', views.live_classes, name='live_classes'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
]
