# Generated by Django 4.0.2 on 2022-03-11 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_forums', '0013_messages_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='updated_at',
            field=models.DateTimeField(verbose_name='Дата редактирования'),
        ),
    ]