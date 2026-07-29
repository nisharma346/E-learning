from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0005_article'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('bio', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
