# Generated by Django 4.2.4 on 2023-08-27 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danbi_app', '0003_subtask_danbi_app_s_team_8ae4d9_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtask',
            name='completed_date',
            field=models.DateTimeField(default=None),
        ),
        migrations.AlterField(
            model_name='task',
            name='completed_date',
            field=models.DateTimeField(default=None),
        ),
    ]