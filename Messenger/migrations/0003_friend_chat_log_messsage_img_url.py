# Generated by Django 3.0.8 on 2020-10-15 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0002_auto_20201015_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend_chat_log',
            name='messsage_img_url',
            field=models.TextField(max_length=1024, null=True),
        ),
    ]