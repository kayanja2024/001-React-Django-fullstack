# Generated by Django 5.1.7 on 2025-04-04 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_adress_customuser_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
