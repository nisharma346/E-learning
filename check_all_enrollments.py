import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_study.settings')
django.setup()

from skill_global.models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

java = Course.objects.filter(slug='complete-java-programming').first()

print(f'Course: {java.title if java else "Not found"}')
print(f'\nAll enrollments for Java Programming:')
for e in CourseEnrollment.objects.filter(course=java):
    print(f'- {e.enrollment_id}: {e.user.email} - {e.payment_status}/{e.order_status}')

print(f'\nAll enrollments in database:')
for e in CourseEnrollment.objects.all().order_by('-created_at'):
    print(f'- {e.enrollment_id}: {e.user.email} - {e.course.title} - {e.payment_status}/{e.order_status} - Created: {e.created_at}')
