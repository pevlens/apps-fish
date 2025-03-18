# Generated by Django 5.1.5 on 2025-03-02 18:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manageappfish', '0012_alter_cacthtg_post_add'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cacthtg',
            name='image',
        ),
        migrations.RemoveField(
            model_name='cacthtg',
            name='image_hash',
        ),
        migrations.CreateModel(
            name='CacthTgImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='tg/')),
                ('image_hash', models.CharField(blank=True, db_index=True, max_length=164, null=True)),
                ('cacthtg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cacth_user_tg', to='manageappfish.cacthtg')),
            ],
        ),
    ]
