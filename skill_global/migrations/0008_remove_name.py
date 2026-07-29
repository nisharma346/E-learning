from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skill_global', '0007_add_auth_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='name',
        ),
    ]
