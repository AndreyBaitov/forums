# Generated by Django 4.0.2 on 2022-03-11 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_forums', '0014_alter_messages_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='topics',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последней записи'),
        ),
    ]
