# Generated by Django 2.1.3 on 2018-12-04 13:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('website', models.URLField()),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='companies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('position', models.CharField(max_length=128)),
                ('city', models.CharField(max_length=85)),
                ('state', models.CharField(max_length=85)),
                ('status', django_fsm.FSMField(default='submitted', max_length=50)),
                ('submitted_date', models.DateField(auto_now_add=True)),
                ('followup_date', models.DateField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to='jobapplication.Company')),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Job Application',
                'verbose_name_plural': 'Job Applications',
            },
        ),
        migrations.CreateModel(
            name='JobReference',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='references', to='jobapplication.Company')),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='references', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Job Reference',
                'verbose_name_plural': 'Job References',
            },
        ),
    ]
