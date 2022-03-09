# Generated by Django 4.0.2 on 2022-03-07 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_forums', '0007_alter_statusers_enter_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusers',
            name='forum',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='forum_stat_users', to='app_forums.forums'),
        ),
        migrations.AddField(
            model_name='statusers',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='topic_stat_users', to='app_forums.topics'),
        ),
    ]
