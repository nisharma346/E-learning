from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def generate_course_slugs(apps, schema_editor):
    Course = apps.get_model('skill_global', 'Course')
    for course in Course.objects.all():
        if not course.slug:
            base_slug = slugify(course.title)[:250]
            slug = base_slug or str(course.id)
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            course.slug = slug
            course.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0011_article_category_article_featured_article_read_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='courseenrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollment_id', models.CharField(editable=False, max_length=36, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_method', models.CharField(blank=True, choices=[('UPI', 'UPI'), ('Card', 'Card'), ('Net Banking', 'Net Banking')], max_length=20)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending', max_length=20)),
                ('order_status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='skill_global.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course Enrollment',
                'verbose_name_plural': 'Course Enrollments',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'course')},
            },
        ),
        migrations.RunPython(generate_course_slugs, reverse_code=migrations.RunPython.noop),
    ]
