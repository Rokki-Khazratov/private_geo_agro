# Generated by Django 5.0.2 on 2024-11-18 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_pendingdeleteplantation'),
    ]

    operations = [
        migrations.AddField(
            model_name='plantation',
            name='is_deleting',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='PendingDeletePlantation',
        ),
    ]
