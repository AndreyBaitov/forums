# Generated by Django 4.0.2 on 2022-03-08 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_profile', '0004_alter_users_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='acknowledgements',
            field=models.IntegerField(default=0, verbose_name='Сколько раз благодарили пользователя'),
        ),
    ]
