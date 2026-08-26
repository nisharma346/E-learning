import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_study.settings')
django.setup()

from skill_global.models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

# Get the latest enrollment
latest = CourseEnrollment.objects.all().order_by('-created_at').first()

if latest:
    print(f'Latest Enrollment:')
    print(f'Enrollment ID: {latest.enrollment_id}')
    print(f'User: {latest.user.email}')
    print(f'Course: {latest.course.title}')
    print(f'Status: {latest.payment_status} / {latest.order_status}')
    print(f'Amount: {latest.amount}')
    print(f'Payment Method: {latest.payment_method}')
    print(f'Razorpay Order ID: {latest.razorpay_order_id}')
    print(f'Razorpay Payment ID: {latest.razorpay_payment_id}')
    print(f'Razorpay Signature: {latest.razorpay_signature[:20] + "..." if latest.razorpay_signature else None}')
    print(f'Created At: {latest.created_at}')
    print(f'Updated At: {latest.updated_at}')
else:
    print('No enrollments found')

# Check Data Analytics course
data_analytics = Course.objects.filter(slug='data-analytics-with-excel-power-bi').first()
if data_analytics:
    print(f'\nData Analytics Course Enrollments:')
    for e in CourseEnrollment.objects.filter(course=data_analytics):
        print(f'- {e.enrollment_id}: {e.user.email} - {e.payment_status}/{e.order_status} - Created: {e.created_at}')
