# Generated by Django 5.0.2 on 2024-11-19 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_plantation_prev_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='plantation',
            name='owner_number',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
