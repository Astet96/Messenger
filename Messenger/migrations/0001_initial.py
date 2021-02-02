# Generated by Django 3.0.8 on 2020-10-13 14:50

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend_Chat_Ledger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Group_Chat_Ledger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=32)),
                ('group_image', models.ImageField(default='groups/default-group-icon.png', storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\alexs\\Desktop\\Capstone - Messenger\\Capstone\\media/'), upload_to='groups')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('profile_image', models.ImageField(default='users/default-profile-icon.jpg', storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\alexs\\Desktop\\Capstone - Messenger\\Capstone\\media/'), upload_to='users')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_type', models.SmallIntegerField()),
                ('var1', models.CharField(max_length=32)),
                ('var2', models.CharField(max_length=32)),
                ('notified_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group_Chat_Participants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_privilege', models.PositiveSmallIntegerField(default=0)),
                ('chat_ledger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Messenger.Group_Chat_Ledger')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group_Chat_Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_txt', models.TextField(max_length=1024, null=True)),
                ('message_img', models.ImageField(blank=True, null=True, upload_to='messages')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat_ledger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Messenger.Group_Chat_Ledger')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_2', to=settings.AUTH_USER_MODEL)),
                ('friend2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_1', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friend_Chat_Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_txt', models.TextField(max_length=1024, null=True)),
                ('message_img', models.ImageField(blank=True, null=True, upload_to='messages')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat_ledger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Messenger.Friend_Chat_Ledger')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='friend_chat_ledger',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friend_chat_ledger',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_1', to=settings.AUTH_USER_MODEL),
        ),
    ]
