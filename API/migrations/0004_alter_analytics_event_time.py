# Generated by Django 3.2.7 on 2021-10-17 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_alter_analytics_event_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analytics_event',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
