# Generated by Django 5.0.2 on 2024-02-26 07:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.CharField(max_length=20, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('major', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('total_attendance', models.IntegerField(default=0)),
                ('last_attendance_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('starting_year', models.DateField()),
                ('standing', models.CharField(max_length=50)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
