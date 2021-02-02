from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_ledger>\w+)/(?P<chat_type>\w+)/$', consumers.Chat_Consumer),
    re_path(r'ws/contact_list/$', consumers.Contact_List_Consumer),
]