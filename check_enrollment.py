import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_study.settings')
django.setup()

from skill_global.models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.first()
java = Course.objects.filter(slug='complete-java-programming').first()

print(f'User: {user.email}')
print(f'Course: {java.title if java else "Not found"}')

enrollment = CourseEnrollment.objects.filter(user=user, course=java).first()

if enrollment:
    print(f'Enrollment ID: {enrollment.enrollment_id}')
    print(f'Status: {enrollment.payment_status} / {enrollment.order_status}')
    print(f'Amount: {enrollment.amount}')
    print(f'Razorpay Order ID: {enrollment.razorpay_order_id}')
    print(f'Razorpay Payment ID: {enrollment.razorpay_payment_id}')
    print(f'Razorpay Signature: {enrollment.razorpay_signature[:20] + "..." if enrollment.razorpay_signature else None}')
else:
    print('No enrollment found for this user and course')

print('\nAll enrollments for user:')
for e in CourseEnrollment.objects.filter(user=user):
    print(f'- {e.course.title}: {e.payment_status}/{e.order_status}')
