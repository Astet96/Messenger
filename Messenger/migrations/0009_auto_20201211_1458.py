# Generated by Django 3.0.8 on 2020-12-11 12:58

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0008_auto_20201103_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group_chat_ledger',
            name='group_image',
            field=models.ImageField(default='groups/default-group-icon.png', storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\alexs\\Desktop\\backup\\cs projects\\Capstone - Messenger\\Capstone\\media/'), upload_to='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(default='users/default-profile-icon.jpg', storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\alexs\\Desktop\\backup\\cs projects\\Capstone - Messenger\\Capstone\\media/'), upload_to='users'),
        ),
    ]