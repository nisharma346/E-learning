from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:id>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.course_enroll, name='course_enrollment'),
    path('courses/my-courses/', views.my_courses, name='my_courses'),
    path('enrollment/success/<str:enrollment_id>/', views.enrollment_success, name='enrollment_success'),
    path('enrollment/invoice/<str:enrollment_id>/', views.enrollment_invoice, name='enrollment_invoice'),
    path(
    'payment/razorpay/verify/',
    views.razorpay_verify,
    name='razorpay_verify'
),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('articles/', views.articles, name='articles'),
    path(
    'articles/<slug:slug>/',
    views.article_detail,
    name='article_detail'
),
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
