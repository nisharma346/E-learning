from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0008_remove_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=150)),
                ('designation', models.CharField(blank=True, max_length=150)),
                ('review', models.TextField()),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='testimonials/')),
                ('verified', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Testimonial',
                'verbose_name_plural': 'Testimonials',
                'ordering': ['-id'],
            },
        ),
    ]
