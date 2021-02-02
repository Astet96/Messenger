from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("register", views.register, name='register'),
    path("login", views.login_view, name='login'),
    path("logout", views.logout_view, name='logout'),

    #API URL's
    path("search_engine/<str:query>", views.search_engine, name="search_engine"),
    path("render_contact_list", views.render_contact_list, name="render_contact_list"),
    path("add_friend/<int:user_id>", views.add_friend, name="add_friend"),
    path("remove_friend_request/<int:user_id>", views.remove_friend_request, name="remove_friend_request"),
    path("load_notifications", views.load_notifications, name="load_notifications"),
    path("remove_notification/<int:notif_type>/<int:notif_user>/<int:var1>/<int:var2>", views.remove_notification, name="remove_notification"),
    path("remove_notification/<int:notif_type>/<int:notif_user>/<int:var1>/<str:var2>", views.remove_notification, name="remove_notification"),
    path("friend_request_response/<int:user_id>/<int:sender_id>/<int:option>", views.friend_request_response, name="friend_request_response"),
    path("get_default_group_image", views.get_default_group_image, name="get_default_group_image"),
    path("add_group_list/<str:contact>", views.add_group_list, name="add_group_list"),
    path("add_user_to_group/<int:friend_id>/<int:group_id>", views.add_user_to_group, name="add_user_to_group"),
    path("new_group_url/<int:friend_id>", views.new_group_url, name="new_group_url"),
    path("create_group/<int:friend_id>", views.create_group, name="create_group"),
    path("get_Friend_Chat_Ledger/<int:friend_id>", views.get_Friend_Chat_Ledger, name="get_Friend_Chat_Ledger"),
    path("chat_img_upload/<int:chat_ledger>/<int:chat_type>", views.chat_img_upload, name="chat_img_upload"),
    path("get_user_id", views.get_user_id, name="get_user_id"),
    path("get_username/<int:user_id>", views.get_username, name="get_username"),
    path("get_groupname/<int:group_id>", views.get_groupname, name="get_groupname"),
    path("remove_friend/<int:friend_id>", views.remove_friend, name="remove_friend"),
    path("exit_group/<int:group_id>", views.exit_group, name="exit_group"),
    path("get_user_privilege/<int:group_id>", views.get_user_privilege, name="get_user_privilege"),
    path("get_friend_list/<int:group_id>", views.get_friend_list, name="get_friend_list"),
    path("get_member_list/<int:group_id>", views.get_member_list, name="get_member_list"),
    path("remove_from_group/<int:user_id>/<int:group_id>", views.remove_from_group, name="remove_from_group"),
    path("change_privilege/<int:user_id>/<int:group_id>/<int:option>", views.change_privilege, name="change_privilege"),
    path("group_change_name/<int:group_id>", views.group_change_name, name="group_change_name"),
    path("group_change_img/<int:group_id>", views.group_change_img, name="group_change_img"),
    path("profile_pic_change", views.profile_pic_change, name="profile_pic_change"),
    path("make_chat_notification/<int:chat_id>/<int:chat_type>/<int:message_type>", views.make_chat_notification, name="make_chat_notification")
]