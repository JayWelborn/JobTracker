# Generated by Django 2.1.3 on 2018-12-04 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobapplication', '0004_auto_20181204_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='rejected_state',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
