# Generated by Django 4.2.4 on 2023-08-27 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danbi_app', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['team'], name='danbi_app_t_team_efd057_idx'),
        ),
    ]
