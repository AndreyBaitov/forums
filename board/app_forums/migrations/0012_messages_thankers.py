# Generated by Django 4.0.2 on 2022-03-08 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_profile', '0002_users_ninja'),
        ('app_forums', '0011_alter_statusers_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='thankers',
            field=models.ManyToManyField(blank=True, related_name='thankers', to='app_profile.Users', verbose_name='Сказавшие спасибо'),
        ),
    ]
