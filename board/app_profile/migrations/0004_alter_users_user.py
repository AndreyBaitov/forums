# Generated by Django 4.0.2 on 2022-03-08 20:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_profile', '0003_users_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='user',
            field=models.OneToOneField(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='app_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
