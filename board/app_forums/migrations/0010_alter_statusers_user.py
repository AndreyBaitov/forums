# Generated by Django 4.0.2 on 2022-03-08 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_profile', '0002_users_ninja'),
        ('app_forums', '0009_alter_statusers_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusers',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stat_users', related_query_name='stat_user', to='app_profile.users'),
        ),
    ]
