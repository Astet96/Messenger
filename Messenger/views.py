import random

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q
from .models import User, Friendship, Friend_Chat_Log, Notification, Group_Chat_Ledger, Group_Chat_Participants, Group_Chat_Log

def rand():
    return random.randint(1,999999)

# this function checks that the password is complex enough (minimum 8 characters, includes number, lower case and upper case characters)
def is_complex(password):
    n = len(password)
    lower = 0
    upper = 0
    number = 0
    check = 0
    if n >= 8:
        for i in range(n):
            if lower == 0:
                if password[i].islower():
                    lower = 1
                    check += 1
            if upper == 0:
                if password[i].isupper():
                    upper = 1
                    check += 1
            if number == 0:
                if password[i].isnumeric():
                    number = 1
                    check += 1
            if check == 3:
                return 1
    return 0

# view function for new account registration
# a future improvement would be to validate the user's email adress
def register(request):
    if request.method == 'POST':
        errors = []
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password_2 = request.POST['password_confirmation']
        if password == "":
            errors.append("Password can't be blank")
            return render(request, 'Messenger/register.html', {
                "random": rand(),
                "errors": errors
            })
        if password != password_2:
            errors.append('Passwords must match')
            return render(request, 'Messenger/register.html', {
                "random": rand(),
                "errors": errors
            })
        if not is_complex(password):
            errors.append('Password not strong enough!')
            return render(request, 'Messenger/register.html', {
                "random": rand(),
                "errors": errors
            })
        try:
            try:
                profile_image = request.FILES['profile_img']
                user = User.objects.create_user(username, email, password, profile_image=profile_image)
            except:
                user = User.objects.create_user(username, email, password)
        except IntegrityError:
            errors.append('User already exists')
            return render(request, 'Messenger/register.html', {
                "random": rand(),
                "errors": errors
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, 'Messenger/register.html', {
            "random": rand
        })

# view function for logging in
def login_view(request):
    if request.method == "POST":
        errors = []
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        try:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        except:
            errors.append('Invalid credentials')
            return render(request, 'Messenger/login.html', {
                "random": rand(),
                "errors": errors
            })
    else:
        return render(request, 'Messenger/login.html', {
            "random": rand()
        })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def index(request):
    return render(request, 'Messenger/index.html', {
        "random": rand()
    })

# Helper function for validating friendships
# Returns the count of friendship links between 2 users, should be either 0 or 1
def friendship_validator(user, friend):
    return Friendship.objects.filter(Q(Q(friend1 = user) & Q(friend2 = friend)) | Q(Q(friend2 = user) & Q(friend1 = friend))).count()

# API functions:

# Gets top 10 results for a query (search for users)
@login_required
def search_engine(request, query):
    current_user = request.user
    results = User.objects.filter(username__icontains = query).exclude(id = current_user.id)
    response_names = [] * 0
    response_pics = [] * 0
    user_ids = [] * 0
    request_sent = [] * 0
    i = 0
    counter = 0
    top = results.count()
    while counter < top:
        if not friendship_validator(current_user, results[i]):
            user_ids.append(results[i].id)
            response_names.append(results[i].username)
            response_pics.append(results[i].profile_image.url)
            # Find out if friend request was already sent
            try:
                Notification.objects.get(notif_type='0', notified_user = User.objects.get(id=user_ids[i]), var1 = request.user.id)
                request_sent.append(1)
            except:
                request_sent.append(0)
            counter+=1
            if counter == 10:
                break
        i+=1
        if i == top:
            break

    return JsonResponse({
        "results_names": response_names,
        "results_pics": response_pics,
        "user_id": user_ids,
        "request_sent": request_sent,
        "counter": counter
    })

# Notifications
@login_required
def load_notifications(request):
    notif = Notification.objects.filter(notified_user=request.user)
    counter = notif.count()
    if counter > 0:
        sw = True
        while sw:
            notified_user = []
            notified_group = []
            notif_type = []
            var1 = []
            var2 = []
            for i in range(counter):
                try:    # solves a bug in retreiving notifications if a user deletes thair acount under specific circumstances due to race conditions
                    notified_user.append(notif[i].notified_user.id)
                    notif_type.append(notif[i].notif_type)
                    var1.append(notif[i].var1)
                    if notif_type[i] in [3, 4, 5, 6, 7]:
                        var2.append(notif[i].var2)
                    elif notif_type[i] in [0, 1, 2]:
                        var2.append(User.objects.get(id = notif[i].var1).username)
                    if notif_type[i] == 4:
                        notified_group.append(notif[i].notified_group.id)
                    else:
                        notified_group.append('-1')
                    if notif_type[i] in [0, 1, 2, 3, 4, 7]:
                        test = User.objects.get(id = notif[i].var1).username
                    # notif_group is appended with '-1' so that the group notification index will be synced up
                    # if this was not done, than the array of group notifications would be likely shorter than the other notifications array
                    # and would cause problems inside javascript when attempting to render these correctly
                    # by using -1 for all non-group notifications, the index will stay inline for all notifications, allowing for a direct pass from start to end without needing further logic checks
                except:
                    Notification.objects.get(id = notif[i].id).delete()
                    break
            sw = False
        notif = Notification.objects.filter(notified_user=request.user)
        counter = notif.count()
        if counter == 0:
            return JsonResponse({
                "counter": counter
            })
    else:
        return JsonResponse({
            "counter": counter
        })

    return JsonResponse({
        "notif_type": notif_type,
        "notified_user": notified_user,
        "notified_group": notified_group,
        "var1": var1,
        "var2": var2,
        "counter": counter
    })

# Send Friend Request
@login_required
def add_friend(request, user_id):
    created = False
    recipient = None
    if user_id != request.user.id and not friendship_validator(request.user, User.objects.get(id=user_id)):
        notif, created = Notification.objects.get_or_create(notif_type='0', notified_user=User.objects.get(id=user_id), var1=request.user.id, var2='0')
        recipient = notif.notified_user.username
    return JsonResponse({
        "created": created,
        "recipient": recipient
    })

@login_required
def remove_friend_request(request, user_id):
    try:
        Notification.objects.filter(notif_type='0', notified_user=User.objects.get(id=user_id), var1=request.user.id).delete()
        removed = True
    except:
        removed = False
    return JsonResponse({
        "removed": removed
    })

@login_required
def remove_notification(request, notif_type, notif_user, var1, var2):
    try:
        if notif_type in [1, 2]:
            Notification.objects.filter(notif_type=notif_type, notified_user=User.objects.get(id=notif_user), var1=var1).delete()
        if notif_type in [3, 5, 6, 7]:
            Notification.objects.filter(notif_type=notif_type, notified_user=User.objects.get(id=notif_user), var1=var1, var2=var2).delete()
        if notif_type == 4:
            Notification.objects.filter(notif_type=notif_type, notified_user=request.user ,notified_group=Group_Chat_Ledger.objects.get(id=notif_user), var1=var1, var2=var2).delete()
        removed = True
    except:
        removed = False
    return JsonResponse({
        "removed": removed
    })

# Respond to friend request
@login_required
def friend_request_response(request, user_id, sender_id, option):
    status = False
    sender= ""
    if user_id == request.user.id:
        try:
            if option: # Create Friendship link if request is accepted
                Friendship.objects.create(friend1 = User.objects.get(id = user_id), friend2 = User.objects.get(id = sender_id))
                Notification.objects.create(notif_type = '1', notified_user = User.objects.get(id = sender_id), var1 = user_id)
            else:
                Notification.objects.create(notif_type = '2', notified_user = User.objects.get(id = sender_id), var1 = user_id)
            Notification.objects.filter(notif_type='0', notified_user=User.objects.get(id=user_id), var1=sender_id).delete()
            sender = User.objects.get(id = sender_id).username
            status = True
        except:
            pass
    return JsonResponse({
        "processed": status,
        "sender": sender
    })

@login_required
def remove_friend(request, friend_id):
    user = request.user
    friend = User.objects.get(id = friend_id)
    if friendship_validator(user, friend):
        try:
            try:
                friendship = Friendship.objects.get(friend1 = user, friend2 = friend)
            except:
                friendship = Friendship.objects.get(friend1 = friend, friend2 = user)
        except:
            return JsonResponse({
                "success": False
            })
        chat_log = Friend_Chat_Log.objects.filter(chat_ledger = friendship)
        counter = chat_log.count() - 1
        # line by line deletion of all chat massages is required in order to properly remove all image files from the file system
        for i in range(counter, 0, -1):
            chat_log[i].delete()
        friendship.delete()
        if not friendship_validator(user, friend):
            Notification.objects.create(notif_type = 7, notified_user = friend, var1 = user.id, var2 = user.username)
            return JsonResponse({
                "success": True
            })
    return JsonResponse({
        "success": False
    })

# this function returns the new group url with the friend_id kwarg
# this allows users to create new groups by selecting an existing friendship
# this is required in order to allow the javascript code to populate the api links and allow for group creation
@login_required
def new_group_url(request, friend_id):
    return JsonResponse({
        "url": reverse("create_group", args=[friend_id])
    })

@login_required
@csrf_exempt
def create_group(request, friend_id):
    user = request.user
    friend = User.objects.get(id = friend_id)
    group_name = request.POST['group_name']
    if friendship_validator(user, friend) and group_name != '':
        try:
            try:
                group_image = request.FILES['group_img']
                group = Group_Chat_Ledger.objects.create(group_name = group_name, group_image = group_image)
            except:
                group = Group_Chat_Ledger.objects.create(group_name = group_name)
            Group_Chat_Participants.objects.create(chat_ledger = group, user = user, user_privilege = 2)
            Group_Chat_Participants.objects.create(chat_ledger = group, user = friend)
            Notification.objects.create(notif_type = 5, notified_user = friend, var1 = group.id, var2 = group.group_name)
            return JsonResponse({
                "success": 1,
                "group_id": group.id
            })
        except:
            return JsonResponse({
                "success": 0
            })
    return JsonResponse({
        "success": 0
    })

@login_required
def get_default_group_image(request):
    return JsonResponse({
        "url": settings.MEDIA_URL + Group_Chat_Ledger._meta.get_field('group_image').default
    })

# this function populates the list of all available groups that a user can add their friends to
@login_required
def add_group_list(request, contact):
    user = request.user
    target = User.objects.get(id = contact.replace('group_add_', ''))
    add_groups_ids = [] * 0
    add_groups_names = [] * 0
    add_groups_imgs = [] * 0
    target_group_list = Group_Chat_Participants.objects.filter(user = target).values('chat_ledger')
    user_group_list = Group_Chat_Participants.objects.filter(Q(user = user) & Q(user_privilege__gte = 1)).exclude(chat_ledger__in=target_group_list)
    groups = user_group_list.count()
    for i in range(groups):
        add_groups_ids.append(user_group_list[i].chat_ledger.id)
        add_groups_names.append(user_group_list[i].chat_ledger.group_name)
        add_groups_imgs.append(user_group_list[i].chat_ledger.group_image.url)
    return JsonResponse({
        "add_groups_ids": add_groups_ids,
        "add_groups_names": add_groups_names,
        "add_groups_imgs": add_groups_imgs
    })

@login_required
def add_user_to_group(request, friend_id, group_id):
    user = request.user
    friend = User.objects.get(id = friend_id)
    group = Group_Chat_Ledger.objects.get(id = group_id)
    try:
        privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege
    except:
        return JsonResponse({
            'success': False
        })
    # Check if friendship and privilege are valid
    if friendship_validator(user, friend) and privilege >= 1:
        Group_Chat_Participants.objects.create(chat_ledger = group, user = friend, user_privilege = 0)
        Notification.objects.create(notif_type = 5, notified_user = friend, var1 = group.id, var2 = group.group_name)
        return JsonResponse({
            'success': True
        })
    return JsonResponse({
        'success': False
    })

# Render Friendlist & Grouplist
def render_contact_list(request):
    user = request.user
    if user.is_authenticated:
        friend_names = [] * 0
        friend_ids = [] * 0
        friend_imgs = [] * 0
        group_names = [] * 0
        group_ids = [] * 0
        group_imgs = [] * 0
        friend_read = Friendship.objects.filter(Q(friend1 = user) | Q(friend2 = user))
        counter = friend_read.count()
        for i in range(counter):
            if(friend_read[i].friend1 == user):
                friend_names.append(friend_read[i].friend2.username)
                friend_ids.append(friend_read[i].friend2.id)
                friend_imgs.append(friend_read[i].friend2.profile_image.url)
            else:
                friend_names.append(friend_read[i].friend1.username)
                friend_ids.append(friend_read[i].friend1.id)
                friend_imgs.append(friend_read[i].friend1.profile_image.url)
        group_read = Group_Chat_Participants.objects.filter(user = user)
        counter = group_read.count()
        for i in range(counter):
            group_names.append(group_read[i].chat_ledger.group_name)
            group_ids.append(group_read[i].chat_ledger.id)
            group_imgs.append(group_read[i].chat_ledger.group_image.url)
        return JsonResponse({
            "friend_names": friend_names,
            "friend_ids": friend_ids,
            "friend_imgs": friend_imgs,
            "group_names": group_names,
            "group_ids": group_ids,
            "group_imgs": group_imgs,
            "logged_in": 1
        })
    return JsonResponse({
        "logged_in": 0
    })

def get_Friend_Chat_Ledger (request, friend_id):
    user = request.user
    friend = User.objects.get(id = friend_id)
    if friendship_validator(user, friend):
        try:
            friend_chat_id = Friendship.objects.get(Q(Q(friend1 = user) & Q(friend2 = friend)) | Q(Q(friend2 = user) & Q(friend1 = friend))).id
        except:
            friend_chat_id = Friendship.objects.create(friend1 = user, friend2 = friend).id
        return JsonResponse({
            "success": True,
            "friend_chat_id": friend_chat_id
        })
    return JsonResponse({
        "success": False
    })

def get_user_id(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "user_id": request.user.id
        })
    else:
        return JsonResponse({
            "user_id": '-1'
        })

@login_required
def get_username(request, user_id):
    return JsonResponse({
        "username": User.objects.get(id = user_id).username
    })

@login_required
def get_groupname(request, group_id):
    return JsonResponse({
        "groupname": Group_Chat_Ledger.objects.get(id = group_id).group_name
    })

@login_required
def get_user_privilege(request, group_id):
    group = Group_Chat_Ledger.objects.get(id = group_id)
    return JsonResponse({
        "user_privilege": Group_Chat_Participants.objects.get(chat_ledger = group, user = request.user).user_privilege
    })

@login_required
def exit_group(request, group_id):
    group = Group_Chat_Ledger.objects.get(id = group_id)
    try:
        Group_Chat_Participants.objects.get(chat_ledger = group, user = request.user).delete()
        delete = False
        # if no admins remain, all mods are elevated to admin level
        if Group_Chat_Participants.objects.filter(chat_ledger = group, user_privilege = 2).count() == 0:
            mods = Group_Chat_Participants.objects.filter(chat_ledger = group, user_privilege = 1)
            if mods.count() > 0:
                mods.update(user_privilege = 2)
            # if no mods exist, then all users become admin:
            if Group_Chat_Participants.objects.filter(chat_ledger = group, user_privilege = 2).count() == 0:
                members = Group_Chat_Participants.objects.filter(chat_ledger = group, user_privilege = 0)
                if members.count() > 0:
                    members.update(user_privilege = 2)
            #if no users exist, group is deleted:
            if Group_Chat_Participants.objects.filter(chat_ledger = group, user_privilege = 2).count() == 0:
                delete = True
        return JsonResponse({
            "success": True,
            "delete": delete
        })
    except:
        pass
    return JsonResponse({
        "success": False
    })

@login_required
@csrf_exempt
def chat_img_upload (request, chat_ledger, chat_type):
    user = request.user
    if chat_type == 1:
        chat_id = Friendship.objects.get(id = chat_ledger)
        if chat_id.friend1 == user:
            friend = chat_id.friend2
        else:
            friend = chat_id.friend1
        if friendship_validator(user, friend):
            try:
                image = request.FILES['image_to_send']
                message = Friend_Chat_Log.objects.create(chat_ledger = chat_id, user = user, message_img = image)
                img_url = message.message_img.url
                message.messsage_img_url = img_url
                message.save()
                return JsonResponse({
                    "success": 1,
                    "img_url": img_url
                })
            except:
                return JsonResponse({
                    "success": 0
                })
        return JsonResponse({
            "success": 0
        })
    else:
        chat_id = Group_Chat_Ledger.objects.get(id = chat_ledger)
        # Check that user is member of the group chat
        if Group_Chat_Participants.objects.filter(chat_ledger = chat_id, user = user).count() == 1:
            try:
                image = request.FILES['image_to_send']
                message = Group_Chat_Log.objects.create(chat_ledger = chat_id, user = user, message_img = image)
                img_url = message.message_img.url
                message.messsage_img_url = img_url
                message.save()
                return JsonResponse({
                    "success": 1,
                    "img_url": img_url
                })
            except:
                return JsonResponse({
                    "success": 0
                })
        return JsonResponse({
            "success": 0
        })

@login_required
def get_friend_list(request, group_id):
    user = request.user
    friend_names = [] * 0
    friend_ids = [] * 0
    friend_imgs = [] * 0
    friends = Friendship.objects.filter(Q(friend1 = user) | Q(friend2 = user))
    group = Group_Chat_Ledger.objects.get(id = group_id)
    test = Group_Chat_Participants.objects.filter(chat_ledger = group, user = user, user_privilege__gte = 1)
    if test.count() == 1:
        counter = friends.count()
        for i in range(counter):
            if(friends[i].friend1 == user):
                if Group_Chat_Participants.objects.filter(chat_ledger = group, user = friends[i].friend2).count() == 0:
                    friend_names.append(friends[i].friend2.username)
                    friend_ids.append(friends[i].friend2.id)
                    friend_imgs.append(friends[i].friend2.profile_image.url)
            else:
                if Group_Chat_Participants.objects.filter(chat_ledger = group, user = friends[i].friend1).count() == 0:
                    friend_names.append(friends[i].friend1.username)
                    friend_ids.append(friends[i].friend1.id)
                    friend_imgs.append(friends[i].friend1.profile_image.url)
    return JsonResponse({
        "friend_names": friend_names,
        "friend_ids": friend_ids,
        "friend_imgs": friend_imgs
    })

# this function returns a list of all group members that the user has the required privilege to remove
@login_required
def get_member_list(request, group_id):
    group = Group_Chat_Ledger.objects.get(id = group_id)
    user = request.user
    member_names = [] * 0
    member_ids = [] * 0
    member_imgs = [] * 0
    member_privilege = [] * 0
    try:
        user_privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege
    except:
        return JsonResponse({
            "member_names": member_names,
            "member_ids": member_ids,
            "member_imgs": member_imgs
        })
    if user_privilege == 0:
        return JsonResponse({
            "member_names": member_names,
            "member_ids": member_ids,
            "member_imgs": member_imgs
        })
    members = Group_Chat_Participants.objects.filter(chat_ledger = group).exclude(user = user)
    if user_privilege == 1:
        members.exclude(user_privilege__gte = 1)
    counter = members.count()
    if counter == 0:
        return JsonResponse({
            "member_names": member_names,
            "member_ids": member_ids,
            "member_imgs": member_imgs
        })
    for i in range(counter):
        member_names.append(members[i].user.username)
        member_ids.append(members[i].user.id)
        member_imgs.append(members[i].user.profile_image.url)
        member_privilege.append(members[i].user_privilege)
    return JsonResponse({
        "member_names": member_names,
        "member_ids": member_ids,
        "member_imgs": member_imgs,
        "member_privilege": member_privilege
    })

@login_required
def remove_from_group(request, user_id, group_id):
    user = request.user
    member = User.objects.get(id = user_id)
    group = Group_Chat_Ledger.objects.get(id = group_id)
    try:
        privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege
        member_privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = member).user_privilege
    except:
        return JsonResponse({
            'success': False
        })
    # Check if privilege and membership are valid
    if privilege == 2 or (privilege == 1 and member_privilege == 0):
        Notification.objects.create(notif_type = 6, notified_user = member, var1 = group.id, var2 = group.group_name)
        Group_Chat_Participants.objects.get(chat_ledger = group, user = member).delete()
        return JsonResponse({
            'success': True
        })
    return JsonResponse({
        'success': False
    })

@login_required
def change_privilege(request, user_id, group_id, option):
    user = request.user
    member = User.objects.get(id = user_id)
    group = Group_Chat_Ledger.objects.get(id = group_id)
    try:
        privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege
        member_privilege = Group_Chat_Participants.objects.get(chat_ledger = group, user = member)
    except:
        return JsonResponse({
            'success': False
        })
    if privilege == 2:
        if option in [0, 1, 2]:
            member_privilege.user_privilege = option
            member_privilege.save()
            return JsonResponse({
                'success': True
            })
    return JsonResponse({
        'success': False
    })

@login_required
@csrf_exempt
def group_change_name(request, group_id):
    user = request.user
    group = Group_Chat_Ledger.objects.get(id = group_id)
    group_name = request.POST['group_name']
    if Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege == 2:
        group.group_name = group_name
        group.save()
        return JsonResponse({
            'success': True,
        })
    return JsonResponse({
        'success': False
    })

@login_required
@csrf_exempt
def group_change_img(request, group_id):
    user = request.user
    group = Group_Chat_Ledger.objects.get(id = group_id)
    group_image = request.FILES['group_img']
    if Group_Chat_Participants.objects.get(chat_ledger = group, user = user).user_privilege == 2:
        group.image_delete()
        group.group_image = group_image
        group.save()
        return JsonResponse({
            'success': True,
            'group_id': group.id
        })
    return JsonResponse({
        'success': False
    })

@login_required
@csrf_exempt
def profile_pic_change(request):
    user = request.user
    profile_image = request.FILES['profile_pic']
    try:
        user.image_delete()
        user.profile_image = profile_image
        user.save()
        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'img_url': user.profile_image.url
        })
    except:
        return JsonResponse({
            'success': False
        })

@login_required
def make_chat_notification(request, chat_id, chat_type, message_type):
    sender = request.user
    if chat_type == 1:
        receiver = User.objects.get(id = chat_id)
        notif, created = Notification.objects.get_or_create(notif_type = 3, notified_user = receiver, var1 = sender.id)
        notif.var2 = message_type
        notif.save()
        return JsonResponse({
            'success': True,
            'created': created
        })
    elif chat_type == 2:
        group = Group_Chat_Ledger.objects.get(id = chat_id)
        users = Group_Chat_Participants.objects.filter(chat_ledger = group)
        this_user = request.user
        for i in range(users.count()):
            if users[i].user != this_user:
                notif, created = Notification.objects.get_or_create(notif_type = 4, notified_user=users[i].user , notified_group = group, var1 = sender.id)
                notif.var2 = message_type
                notif.save()
        return JsonResponse({
            'success': True
        })
    return JsonResponse({
        'success': False
    })