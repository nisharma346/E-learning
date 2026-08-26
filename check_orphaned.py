import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_study.settings')
django.setup()

from skill_global.models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

enrollments = CourseEnrollment.objects.all()
print(f'Total enrollments: {enrollments.count()}')
print(f'Total users: {User.objects.count()}')
print(f'Total courses: {Course.objects.count()}')
print('\nChecking for orphaned enrollments...')

for e in enrollments:
    user_exists = User.objects.filter(id=e.user_id).exists()
    course_exists = Course.objects.filter(id=e.course_id).exists()
    
    if not user_exists or not course_exists:
        print(f'ORPHANED: {e.enrollment_id}')
        print(f'  - User ID: {e.user_id}, User exists: {user_exists}')
        print(f'  - Course ID: {e.course_id}, Course exists: {course_exists}')
        print(f'  - Deleting orphaned enrollment...')
        e.delete()
        print(f'  - Deleted')
    else:
        print(f'OK: {e.enrollment_id} - User: {e.user.email}, Course: {e.course.title}')

print('\nDone!')
