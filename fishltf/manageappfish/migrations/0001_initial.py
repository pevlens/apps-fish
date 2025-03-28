# Generated by Django 5.1.5 on 2025-02-19 17:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserTg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.BigIntegerField(max_length=40, unique=True, verbose_name='id пользователя в телеграмм')),
                ('username', models.CharField(blank=True, max_length=100, null=True, verbose_name='username в TG')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='имя в TG')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='фамилия в TG')),
                ('phone_number', models.IntegerField(blank=True, max_length=40, null=True, unique=True, verbose_name='номер телефона в телеграмм')),
                ('image', models.ImageField(blank=True, null=True, upload_to='tg/')),
                ('metod_catch', models.CharField(blank=True, max_length=100, null=True, verbose_name='основной метод ловли')),
                ('gear_main', models.CharField(blank=True, max_length=100, null=True, verbose_name='оснавная снать')),
                ('bio', models.CharField(blank=True, max_length=100, null=True, verbose_name='об себе ')),
                ('alias', models.CharField(blank=True, max_length=100, null=True, verbose_name='Кличка')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
        ),
        migrations.CreateModel(
            name='CacthTg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='tg/')),
                ('about', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('weight', models.IntegerField(blank=True, null=True, verbose_name='Вес')),
                ('bait', models.TextField(blank=True, null=True, verbose_name='приманка')),
                ('location_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Локация')),
                ('fish', models.CharField(blank=True, max_length=100, null=True, verbose_name='РЫба')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fishman_tg', to='manageappfish.usertg')),
            ],
        ),
    ]
