import json
import datetime

from django.utils import dateparse

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .views import friendship_validator

from django.db.models import Q
from .models import User, Friendship, Friend_Chat_Log, Notification, Group_Chat_Ledger, Group_Chat_Participants, Group_Chat_Log

# Consumer code based on the tutorial & documentation from:
# https://channels.readthedocs.io/en/latest/
# as well as the youtube tutorial from the "JustDjango" channel and his code
# https://www.youtube.com/watch?v=Wv5jlmJs2sU
# https://www.youtube.com/watch?v=xrKKRRC518Y

# The chat consumer is used to send chat messages to and retreive them from the database
# This is done via a Redis server that I have set up on Ubuntu running on the linux subsystem for windows 10
# Redis is essential for this functionality since it handles websockets which are essential for the Channels package to work
class Chat_Consumer(WebsocketConsumer):
    # The connect method connects the user to the corresponding chat socket using the key word arguments passed in the routing url
    # This establishes a connection to the correct chat by determining the "chat type" friend or group, as well as the "chat ledger" id, either the group id or the friend's user id
    # chat_type: 1 = friend chat | 2 = group chat
    # chat_ledger: friend's user id or group chat id depending on chat type
    # in the case of a friend chat, the friendship relationship doubles as the chat ledger, that way if the friendship ends, the chat log is automaticaly deleted
    def connect(self):
        user = self.scope['user']
        if self.scope['url_route']['kwargs']['chat_type'] == '1':
            chat_ledger = Friendship.objects.get(id = self.scope['url_route']['kwargs']['chat_ledger'])
            if chat_ledger.friend1 == user:
                friend = chat_ledger.friend2
            else:
                friend = chat_ledger.friend1
            if friendship_validator(user, friend):
                self.room_name = self.scope['url_route']['kwargs']['chat_ledger']
                self.room_group_name = 'friend_chat_%s' % self.room_name
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name,
                    self.channel_name
                )
                self.chat_ledger = chat_ledger
                self.accept()
        elif self.scope['url_route']['kwargs']['chat_type'] == '2':
            chat_ledger = Group_Chat_Ledger.objects.get(id = self.scope['url_route']['kwargs']['chat_ledger'])
            if Group_Chat_Participants.objects.filter(chat_ledger = chat_ledger, user = user).count() == 1:
                self.room_name = self.scope['url_route']['kwargs']['chat_ledger']
                self.room_group_name = 'group_chat_%s' % self.room_name
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name,
                    self.channel_name
                )
                self.chat_ledger = chat_ledger
                self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # This function retreives the previous 20 messages in the conversation
    # if the start is reached then the 'done' message is sent, letting the JavaScript code know to display the "start of chat" message and stop attempting to retreive messages
    def fetch_previous_messages(self, data):
        if data['timestamp'] == 0:
            if self.scope['url_route']['kwargs']['chat_type'] == '1':
                messages = Friend_Chat_Log.objects.filter(chat_ledger = self.chat_ledger).order_by('-timestamp')[:20]
            elif self.scope['url_route']['kwargs']['chat_type'] == '2':
                messages = Group_Chat_Log.objects.filter(chat_ledger = self.chat_ledger).order_by('-timestamp')[:20]
            content = {
                'command': 'initial_previous_messages',
                'messages': self.messages_to_json(messages)
            }
        else:
            timestamp = dateparse.parse_datetime(data['timestamp'])
            if self.scope['url_route']['kwargs']['chat_type'] == '1':
                messages = Friend_Chat_Log.objects.filter(chat_ledger = self.chat_ledger, timestamp__lt = timestamp).order_by('-timestamp')[:20]
            elif self.scope['url_route']['kwargs']['chat_type'] == '2':
                messages = Group_Chat_Log.objects.filter(chat_ledger = self.chat_ledger, timestamp__lt = timestamp).order_by('-timestamp')[:20]
            if messages.count() != 0:
                content = {
                    'command': 'previous_messages',
                    'messages': self.messages_to_json(messages)
                }
            else:
                content = {
                    'command': 'previous_messages',
                    'messages': 'done'
                }
        self.load_previous_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            if message.message_txt != None:
                result.append(self.text_message_to_json(message))
            if message.messsage_img_url != None:
                result.append(self.img_message_to_json(message))
        return result

    def text_message_to_json(self, message):
        return {
            'message_type': 'text',
            'owner': message.user.id,
            'owner_name':message.user.username,
            'profile_pic': message.user.profile_image.url,
            'text': message.message_txt,
            'timestamp': message.timestamp.__str__()
        }

    def img_message_to_json(self, message):
        return {
            'message_type': 'image',
            'owner': message.user.id,
            'owner_name':message.user.username,
            'profile_pic': message.user.profile_image.url,
            'img': message.messsage_img_url,
            'timestamp': message.timestamp.__str__()
        }

    # this method sends a new text message from a user via the appropriate websocket to all the other users connected,
    # as well as storing it into the database for future retreival
    def send_new_text_message(self, data):
        user = self.scope['user']
        chat_ledger = self.chat_ledger
        if self.scope['url_route']['kwargs']['chat_type'] == '1':
            message = Friend_Chat_Log.objects.create(chat_ledger = chat_ledger, user = user, message_txt = data['message'])
        elif self.scope['url_route']['kwargs']['chat_type'] == '2':
            message = Group_Chat_Log.objects.create(chat_ledger = chat_ledger, user = user, message_txt = data['message'])
        content = {
            'command': 'send_new_text_message',
            'chat_type': self.scope['url_route']['kwargs']['chat_type'],
            'message': self.text_message_to_json(message)
        }
        return self.send_text_chat_message(content)

    # this method sends an immage message via retreiving the file's url from the file storage and passing it to the websocket
    # the handling of the file upload is done via a view api function that is called and completed prior to this method
    def send_new_img_message(self, data):
        user = self.scope['user']
        chat_ledger = self.chat_ledger
        if self.scope['url_route']['kwargs']['chat_type'] == '1':
            message = Friend_Chat_Log.objects.get(chat_ledger = chat_ledger, user = user, messsage_img_url = data['message'])
        elif self.scope['url_route']['kwargs']['chat_type'] == '2':
            message = Group_Chat_Log.objects.get(chat_ledger = chat_ledger, user = user, messsage_img_url = data['message'])
        content = {
            'command': 'send_new_img_message',
            'chat_type': self.scope['url_route']['kwargs']['chat_type'],
            'message': self.img_message_to_json(message)
        }
        return self.send_image_chat_message(content)

    # this way of processing commands is directly taken from the youtube tutorials as it is very convenient
    commands = {
        'fetch_previous_messages': fetch_previous_messages,
        'send_new_text_message': send_new_text_message,
        'send_new_img_message' : send_new_img_message
    }

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_text_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text_data': message
            }
        )

    def send_image_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text_data': message
            }
        )

    def chat_message(self, event):
        message = event['text_data']
        self.send(text_data=json.dumps(message))

    def load_previous_message(self, message):
        self.send(text_data=json.dumps(message))

# This websocket consumer connects all the logged in users so that their contact and group list can be instantly synced up
class Contact_List_Consumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            self.room_name = 'contact_list'
            self.room_group_name = 'render_%s' % self.room_name
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def update_friend_list(self, data):
        users = []
        users.append(data['user'])
        users.append(data['friend'])
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'update_friend_list',
                'users': users
            }
        )

    def update_group_list(self, data):
        users = []
        group = Group_Chat_Ledger.objects.get(id = data['group'])
        participants = Group_Chat_Participants.objects.filter(chat_ledger = group).order_by('-timestamp')[:2]
        for i in range(participants.count()):
            users.append(participants[i].user.id)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'update_group_list',
                'users': users
            }
        )

    def refresh_group_list(self, data):
        users = []
        group = Group_Chat_Ledger.objects.get(id = data['group'])
        participants = Group_Chat_Participants.objects.filter(chat_ledger = group)
        for i in range(participants.count()):
            users.append(participants[i].user.id)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'refresh_group_list',
                'users': users
            }
        )

    def reload_banner(self, data):
        users = []
        group = Group_Chat_Ledger.objects.get(id = data['group'])
        participants = Group_Chat_Participants.objects.filter(chat_ledger = group)
        for i in range(participants.count()):
            users.append(participants[i].user.id)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'reload_banner',
                'users': users,
                'group': data['group'],
                'group_name': data['group_name']
            }
        )

    def update_profile_pic(self, data):
        users = []
        user = data['user']
        img_url = data['img_url']
        friends = Friendship.objects.filter(Q(friend1 = User.objects.get(id = data['user'])) | Q(friend2 = User.objects.get(id = data['user'])))
        for i in range(friends.count()):
            if friends[i].friend1.id == user:
                users.append(friends[i].friend2.id)
            else:
                users.append(friends[i].friend1.id)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'update_profile_pic',
                'user': user,
                'users': users,
                'img_url': img_url
            }
        )

    def delete_user(self, data):
        users = []
        user = User.objects.get(id = data['user'])
        if(user == self.scope['user']):
            # Delete friend chat messages this way to ensure proper removal of images from the file system
            friends = Friendship.objects.filter(Q(friend1 = user) | Q(friend2 = user))
            counter = friends.count() - 1
            for i in range(counter, -1, -1):
                if friends[i].friend1 == user:
                    users.append(friends[i].friend2.id)
                else:
                    users.append(friends[i].friend1.id)
                chat_log = Friend_Chat_Log.objects.filter(chat_ledger = friends[i])
                counter = chat_log.count() - 1
                for j in range(counter, -1, -1):
                    chat_log[j].delete()
                friends[i].delete()

            # Same principle applies to deletion of group messages
            group_messages = Group_Chat_Log.objects.filter(user = user)
            counter = group_messages.count() - 1
            for i in range(counter, -1, -1):
                group_messages[i].delete()
            deleted = user.id
            # Automatic group management: elevate user privileges if no admins remain or delete group if no members remain
            groups = Group_Chat_Participants.objects.filter(user = user)
            counter = groups.count() - 1
            for i in range(counter, -1, -1):
                group_id = groups[i].chat_ledger
                Group_Chat_Participants.objects.get(chat_ledger = group_id, user = user).delete()
                # if no admins remain, all mods are elevated to admin level
                if Group_Chat_Participants.objects.filter(chat_ledger = group_id, user_privilege = 2).count() == 0:
                    mods = Group_Chat_Participants.objects.filter(chat_ledger = group_id, user_privilege = 1)
                    if mods.count() > 0:
                        mods.update(user_privilege = 2)
                    # if no mods exist, then all users become admin:
                    if Group_Chat_Participants.objects.filter(chat_ledger = group_id, user_privilege = 2).count() == 0:
                        members = Group_Chat_Participants.objects.filter(chat_ledger = group_id, user_privilege = 0)
                        if members.count() > 0:
                            members.update(user_privilege = 2)
                    #if no users exist, group is deleted:
                    if Group_Chat_Participants.objects.filter(chat_ledger = group_id, user_privilege = 2).count() == 0:
                        chat_log = Group_Chat_Log.objects.filter(chat_ledger = group_id)
                        cntr = chat_log.count() - 1
                        for i in range(cntr, -1, -1):
                            chat_log[i].delete()
                        group_id.delete()
            user.delete()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'refresh',
                    'command': 'delete_user',
                    'deleted': deleted,
                    'users': users
                }
            )
    
    def user_removed_from_group(self, data):
        users = []
        user = User.objects.get(id = data['user'])
        users.append(user.id)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'user_removed_from_group',
                'group': data['group'],
                'users': users
            }
        )

    def delete_group(self, data):
        users = []
        user = self.scope['user']
        group = Group_Chat_Ledger.objects.get(id = data['group'])
        participants = Group_Chat_Participants.objects.filter(chat_ledger = group)
        participants_count = participants.count()
        if participants_count != 0:
            if Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege == 2:
                for i in range(participants_count):
                    users.append(participants[i].user.id)
                chat_log = Group_Chat_Log.objects.filter(chat_ledger = group)
                counter = chat_log.count() - 1
                if counter != 0:
                    for i in range(counter, 0, -1):
                        chat_log[i].delete()
                group.delete()
        if participants_count == 0:
            chat_log = Group_Chat_Log.objects.filter(chat_ledger = group)
            counter = chat_log.count() - 1
            if counter != 0:
                for i in range(counter, 0, -1):
                    chat_log[i].delete()
            group.delete()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh',
                'command': 'delete_group',
                'group': data['group'],
                'users': users
            }
        )

    commands = {
        'update_friend_list': update_friend_list,
        'update_group_list': update_group_list,
        'refresh_group_list': refresh_group_list,
        'update_profile_pic': update_profile_pic,
        'delete_user': delete_user,
        'delete_group': delete_group,
        'user_removed_from_group': user_removed_from_group,
        'reload_banner': reload_banner
    }

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def refresh(self, message):
        self.send(text_data=json.dumps(message))

# From my understanding this approach to the messanger chat and contact list should be able to work at a larger scale, of maybe tens of thousands of simultaneous users without it crashing:
# https://medium.com/@alexhultman/millions-of-active-websockets-with-node-js-7dc575746a01
# https://stackoverflow.com/questions/61168951/how-much-data-can-a-websocket-consumer-handle