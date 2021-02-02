from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class User(AbstractUser):
    profile_image = models.ImageField(storage=FileSystemStorage(location=settings.MEDIA_ROOT), upload_to='users', default='users/default-profile-icon.jpg')

    def delete(self, *args, **kwargs):
        if self.profile_image != 'users/default-profile-icon.jpg':
            self.profile_image.delete()
        super().delete(*args, **kwargs)

    def image_delete(self, *args, **kwargs):
        if self.profile_image != 'users/default-profile-icon.jpg':
            self.profile_image.delete()

class Friendship(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_2')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_1')

class Friend_Chat_Log(models.Model):
    chat_ledger = models.ForeignKey(Friendship, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_txt = models.TextField(max_length=1024, null=True)
    message_img = models.ImageField(upload_to='101_messages', blank=True, null=True)
    messsage_img_url = models.TextField(max_length=1024, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        self.message_img.delete()
        super().delete(*args, **kwargs)

class Group_Chat_Ledger(models.Model):
    group_name = models.CharField(max_length=32, blank=False, null=False)
    group_image = models.ImageField(storage=FileSystemStorage(location=settings.MEDIA_ROOT), upload_to='groups', default='groups/default-group-icon.png')

    def delete(self, *args, **kwargs):
        if self.group_image != 'groups/default-group-icon.png':
            self.group_image.delete()
        super().delete(*args, **kwargs)

    def image_delete(self, *args, **kwargs):
        if self.group_image != 'groups/default-group-icon.png':
            self.group_image.delete()

class Group_Chat_Participants(models.Model):
    chat_ledger = models.ForeignKey(Group_Chat_Ledger, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_privilege = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # user privilege levels:
    # 0 = read/write messages
    # 1 = can add new users can delete users of privilege 0
    # 2 = admin (can change group icon, group name, user privilege lvls and delete group, can delete users of all privilege lvls)

class Group_Chat_Log(models.Model):
    chat_ledger = models.ForeignKey(Group_Chat_Ledger, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_txt = models.TextField(max_length=1024, null=True)
    message_img = models.ImageField(upload_to='group_messages', blank=True, null=True)
    messsage_img_url = models.TextField(max_length=1024, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        self.message_img.delete()
        super().delete(*args, **kwargs)

class Notification(models.Model):
    notif_type = models.SmallIntegerField(null=False)
    notified_user = models.ForeignKey(User, on_delete=models.CASCADE)
    notified_group = models.ForeignKey(Group_Chat_Ledger, on_delete=models.CASCADE, blank=True, null=True)
    var1 = models.CharField(max_length=32, null=False)
    var2= models.CharField(max_length=32, null=False)

    #   notif_types:
    #   0 = friend request
    #   1 = friend request accepted
    #   2 = friend request declined
    #   3 = new message from friend
    #   4 = new message from group
    #   5 = added to group
    #   6 = removed from group (deleted group)
    #   7 = removed from friends

    #   uses:

    #   friend request:
    #   notified_user => User object of person that is added
    #   var1 => id of user that made the friend request
    #   var2 => not used

    #   friend request accepted:
    #   notified_user => User object of person that made the friend request
    #   var1 => id of user that accepted
    #   var2 => not used

    #   friend request declined:
    #   notified_user => User object of person that made the friend request
    #   var1 => id of user that declined
    #   var2 => not used

    #   new message from friend:
    #   notified_user => User object of person that is messaged
    #   var1 => id of user that made the message
    #   var2 => message type

    #   new message from group:
    #   notified_group => Group object of the group that is messaged
    #   var1 => id of user that made the message
    #   var2 => message type

    #   added to group:
    #   notified_user => User object of the new group member
    #   var1 => group id
    #   var2 => group name

    #   removed from group:
    #   notified_user => User object(s) of the removed group member
    #   var1 => group id
    #   var2 => group name

    #   removed from friends:
    #   notified_user => User object of the removed friend
    #   var1 => id of user that ended friendship
    #   var2 => Name of user that canceled friendship