# Generated by Django 5.0.2 on 2024-11-12 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_plantation_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(default=998989999898, max_length=255),
            preserve_default=False,
        ),
    ]
