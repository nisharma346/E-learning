import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_study.settings')
django.setup()

from skill_global.models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

enrollment = CourseEnrollment.objects.filter(enrollment_id='149AB3A71B294D1098CF').first()

if enrollment:
    print(f'Enrollment ID: {enrollment.enrollment_id}')
    print(f'User: {enrollment.user.email}')
    print(f'Course: {enrollment.course.title}')
    print(f'Status: {enrollment.payment_status} / {enrollment.order_status}')
    print(f'Amount: {enrollment.amount}')
    print(f'Payment Method: {enrollment.payment_method}')
    print(f'Razorpay Order ID: {enrollment.razorpay_order_id}')
    print(f'Razorpay Payment ID: {enrollment.razorpay_payment_id}')
    print(f'Razorpay Signature: {enrollment.razorpay_signature[:20] + "..." if enrollment.razorpay_signature else None}')
    print(f'Created At: {enrollment.created_at}')
    print(f'Updated At: {enrollment.updated_at}')
else:
    print('Enrollment not found')
