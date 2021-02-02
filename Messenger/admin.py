from django.contrib import admin

from .models import User, Friendship, Friend_Chat_Log, Notification, Group_Chat_Ledger, Group_Chat_Participants, Group_Chat_Log

# Register your models here.
admin.site.register(User)
admin.site.register(Friendship)
admin.site.register(Friend_Chat_Log)
admin.site.register(Notification)
admin.site.register(Group_Chat_Ledger)
admin.site.register(Group_Chat_Participants)
admin.site.register(Group_Chat_Log)