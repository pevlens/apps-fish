# Generated by Django 5.1.5 on 2025-02-20 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manageappfish', '0006_telegrammessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertg',
            name='phone_number',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='номер телефона в телеграмм'),
        ),
    ]
