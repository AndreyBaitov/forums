# Generated by Django 4.0.2 on 2022-03-15 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_profile', '0007_users_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='msgs',
            field=models.IntegerField(default=0, verbose_name='Количество сообщений пользователя'),
        ),
        migrations.AddField(
            model_name='users',
            name='thanks',
            field=models.IntegerField(default=0, verbose_name='Сколько раз благодарил сам пользователь'),
        ),
    ]
