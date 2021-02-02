# Generated by Django 3.0.8 on 2020-10-27 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger', '0005_group_chat_participants_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend_chat_log',
            name='chat_ledger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Messenger.Friendship'),
        ),
        migrations.DeleteModel(
            name='Friend_Chat_Ledger',
        ),
    ]