# Generated by Django 5.1.5 on 2025-02-19 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manageappfish', '0003_alter_usertg_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertg',
            name='phone_number',
            field=models.IntegerField(blank=True, max_length=100, null=True, unique=True, verbose_name='номер телефона в телеграмм'),
        ),
    ]
