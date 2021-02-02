var send_message = null;
var send_img_message = null;
var chat_banner = null;
var chat_area = null;
var text_message_content = null;
var contact_list = null;
var search_div = null;
var chat_container = null;
var ChatSocket = null;
var groupchatSocket = null;
var chat_area = null;
var window_width = 0;
var mobile_screen = 1;

// if enter is pressed the chat message is sent
function check_and_send(event){
    if(event.key == 'Enter'){
        document.getElementById('send_text_button').click();
    }
}

function load_previous_messages() {
    var timestamp = null;
    try{
        timestamp = chat_area.getElementsByTagName('div')[0].getAttribute('timestamp');
    }
    catch(err) {}
    if(timestamp != null) {
        ChatSocket.send(JSON.stringify({
            'timestamp': timestamp,
            'command': 'fetch_previous_messages'
        }));
    }
}

function start_scroll() {
    chat_area.scrollTo(0, 1);
}

function togle_empty_chat_overlay(opt) {
    var chat_overlay = document.getElementById('chat_area_overlay');
    if(opt == 1) {
        chat_overlay.classList.add('hidden');
    }
    if(opt == 0) {
        chat_overlay.classList.remove('hidden');
    }
}

// after fetching initial messages, the chat area is scrolled to the bottom and shown to the user
// had to set a timeout and recursive call in order to avoid a bug where the area was scrolled only halfway down when loading image messages
function scroll_bottom(initial) {
    var old_maxScrollTop = 0;
    var new_maxScrollTop = 0;
    setTimeout(() => {old_maxScrollTop = chat_area.scrollHeight - chat_area.offsetHeight;}, 100);
    setTimeout(() => {new_maxScrollTop = chat_area.scrollHeight - chat_area.offsetHeight;}, 200);
    setTimeout(() => {
        if(old_maxScrollTop != new_maxScrollTop) {
            scroll_bottom(initial);
        }
        else {
            if(initial) {
                var unhide_friend_msg = document.getElementsByClassName('friend_message')
                var unhide_self_msg = document.getElementsByClassName('user_message')
                for(i = 0; i < unhide_friend_msg.length; i++) {
                    unhide_friend_msg[i].classList.remove('hidden_message');
                }
                for(i = 0; i < unhide_self_msg.length; i++) {
                    unhide_self_msg[i].classList.remove('hidden_message');
                }
            }
            chat_area.scrollTo(0, new_maxScrollTop);
        }
    }, 300);
}

// when receiving a new message the chat area is automatically scrolled down to bottom, unless the user is reading through old messages (the scrollbar position is more than 50% up)
async function bottom_magnet() {
    var maxScrollTop = chat_area.scrollHeight - chat_area.offsetHeight;
    var position = chat_area.scrollTop;
    if(position/maxScrollTop > 0.5) {
        scroll_bottom(false);
    }
    else if(chat_area.childElementCount <=20){
        scroll_bottom(false);
    }
}

window.addEventListener('DOMContentLoaded', function() {
    menu_items_width();
    start_contact_list_socket();

    send_img_message = document.getElementById('send_image_button');
    send_message = document.getElementById('send_text_button');
    chat_banner = document.getElementById('chatting_with_name');
    chat_area = document.getElementById('chat_area_content');
    text_message_content = document.getElementById('text_message_content');
    chat_area = document.getElementById('chat_area_content');
    try {
        contact_list = document.getElementById('contact_list');
        search_div = document.getElementById('search_div');
        chat_container = document.getElementById('chat_container');
    }
    catch(err){}
    finally{}

    // window width is used to delimitate between mobile and desktop presentation
    window_width = window.innerWidth;
    try {
        if(window_width <= 800) {
            search_div.classList.add('mobile');
            contact_list.classList.add('mobile');
            chat_container.classList.add('mobile');
            search_div.classList.add('disabled');
            contact_list.classList.add('disabled');
            chat_container.classList.remove('disabled');
        }
        else {
            search_div.classList.remove('mobile');
            contact_list.classList.remove('mobile');
            chat_container.classList.remove('mobile');
        }
    }
    catch(err){}
    finally{}
    
    try {
        chat_area.addEventListener('scroll', function() {
            if(chat_area.scrollTop == 0) {
                start_scroll();
                load_previous_messages();
            }
        });
    }
    catch(err){}
    finally{}
});

// on resize checks wether to display mobile or desktop format
window.onresize = () => {
    window_width = window.innerWidth;
    try{
        if(window_width <= 800) {
            search_div.classList.add('mobile');
            contact_list.classList.add('mobile');
            chat_container.classList.add('mobile');
            if(mobile_screen == 1) {
                search_div.classList.add('disabled');
                contact_list.classList.add('disabled');
                chat_container.classList.remove('disabled');
                document.getElementById('chat_area_overlay').classList.remove('contact_search');
                document.getElementById('body_wrapper').classList.remove('contact_search');
            }
            else {
                search_div.classList.remove('disabled');
                contact_list.classList.remove('disabled');
                chat_container.classList.add('disabled');
                document.getElementById('chat_area_overlay').classList.add('contact_search');
                document.getElementById('body_wrapper').classList.add('contact_search');
            }
        }
        else {
            search_div.classList.remove('mobile');
            contact_list.classList.remove('mobile');
            chat_container.classList.remove('mobile');
            chat_container.classList.remove('disabled');
            search_div.classList.remove('disabled');
            contact_list.classList.remove('disabled');
            document.getElementById('chat_area_overlay').classList.remove('contact_search');
            document.getElementById('body_wrapper').classList.remove('contact_search');
        }
    }
    catch(err){}
    finally{}
}

// for mobile show only the contact list
function max_contacts() {
    chat_container.classList.add('disabled');
    search_div.classList.remove('disabled');
    contact_list.classList.remove('disabled');
    document.getElementById('chat_area_overlay').classList.add('contact_search');
    document.getElementById('body_wrapper').classList.add('contact_search');
    mobile_screen = 2;
}

// for mobile show only the chat area
function max_chat() {
    search_div.classList.add('disabled');
    contact_list.classList.add('disabled');
    chat_container.classList.remove('disabled');
    document.getElementById('chat_area_overlay').classList.remove('contact_search');
    document.getElementById('body_wrapper').classList.remove('contact_search');
    mobile_screen = 1;
}

// Hides menu items when colapsed
function menu_items_width() {
    let wth = document.getElementById('navbar_items').offsetWidth
    document.getElementById('navbar_mask').style.width = `${wth}px`;
}

// Animated menu button method from: https://www.w3schools.com/howto/tryit.asp?filename=tryhow_css_menu_icon_js
// Open/Close Menu
function menu_click(x) {
    x.classList.toggle('change');
    let option = document.querySelector('.menu_icon').getAttribute('option');
    if(option === '1') {
        document.getElementById('navbar_items').style.visibility = 'visible';
        document.getElementById('navbar_mask').style.transform='scaleX(0)';
        document.getElementById('nav_menu').setAttribute('option', '0');
    }
    else {
        document.getElementById('navbar_mask').style.transform='scaleX(1)';
        setTimeout(function l(){document.getElementById('navbar_items').style.visibility = 'hidden';}, 400);
        document.getElementById('nav_menu').setAttribute('option', '1');
    }
  }

// Open/Close contact/group list
function contact_list_togle(opt) {
    if(opt === 1) {
        document.querySelector('.friend_list').classList.toggle('displayed');
        document.querySelector('.line1').classList.toggle('change');
        document.querySelector('.line2').classList.toggle('change');
        if(document.querySelector('.friend_list').classList.contains('scroll')) {
            document.querySelector('.friend_list').classList.remove('scroll');
            document.getElementById('group_togle').style.borderTopWidth = '1px';
        }
        else {
            document.getElementById('group_togle').style.borderTopWidth = '0px';
            setTimeout(function l(){document.querySelector('.friend_list').classList.add('scroll');}, 400);
        }
    }
    else {
        document.querySelector('.group_list').classList.toggle('displayed');
        document.querySelector('.line3').classList.toggle('change');
        document.querySelector('.line4').classList.toggle('change');
        if(document.querySelector('.group_list').classList.contains('scroll')) {
            document.querySelector('.group_list').classList.remove('scroll');
        }
        else {
            setTimeout(function l(){document.querySelector('.group_list').classList.add('scroll');}, 400);
        }
    }
}

function update_friend_list(user_id, friend_id) {
    ContactSocket.send(JSON.stringify({
        'user': user_id,
        'friend': friend_id,
        'command': 'update_friend_list'
    }));
}

function update_group_list(group_id) {
    ContactSocket.send(JSON.stringify({
        'group': group_id,
        'command': 'update_group_list'
    }));
}

function refresh_group_list(group_id) {
    ContactSocket.send(JSON.stringify({
        'group': group_id,
        'command': 'refresh_group_list'
    }));
}

function reload_banner(group_id, group_name) {
    ContactSocket.send(JSON.stringify({
        'group': group_id,
        'group_name': group_name,
        'command': 'reload_banner'
    }));
}

function update_profile_pic(user_id, img_url) {
    ContactSocket.send(JSON.stringify({
        'user': user_id,
        'img_url': img_url,
        'command': 'update_profile_pic'
    }));
}

function user_removed_from_group(user_id, group_id) {
    ContactSocket.send(JSON.stringify({
        'user': user_id,
        'group': group_id,
        'command': 'user_removed_from_group'
    }));
}

function delete_user(user_id) {
    ContactSocket.send(JSON.stringify({
        'user': user_id,
        'command': 'delete_user'
    }));
    location.replace("logout");
}

function delete_group(group_id) {
    ContactSocket.send(JSON.stringify({
        'group': group_id,
        'command': 'delete_group'
    }));
    close_overlay();
}

function purge_chat_area() {
    togle_empty_chat_overlay(0)
    chat_banner.innerHTML = '';
    chat_area.innerHTML = '';
    send_img_message.removeAttribute('onClick');
    send_message.removeAttribute('onClick');
    chat_container.removeAttribute('chat_type');
    chat_container.removeAttribute('chat_id');
}

// Contact List socket management
async function start_contact_list_socket() {
    try{
        var user_id = null;
        await fetch('get_user_id')
        .then(response => response.json())
        .then(result => {
            user_id = result['user_id'];
        });
        if(user_id != -1){
            ContactSocket = new WebSocket('ws://' + window.location.host + '/ws/contact_list/');
            ContactSocket.onopen = function() {
                render_contact_list();
            }
            ContactSocket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                for(i = 0; i < data['users'].length; i++) {
                    if(user_id == data['users'][i]) {
                        var chat_type = chat_container.getAttribute('chat_type');
                        var chat_id = chat_container.getAttribute('chat_id');
                        render_contact_list();
                        if(data['command'] == 'update_friend_list' && chat_type == '1') {
                            switch(i) {
                                case 0:
                                    if(chat_id == data['users'][1]) {
                                        purge_chat_area();
                                    }
                                    break;
                                case 1:
                                    if(chat_id == data['users'][0]) {
                                        purge_chat_area();
                                    }
                                    break;
                            }
                        }
                        if(data['command'] == 'reload_banner' && chat_type == '2' && chat_id == data['group']) {
                            document.getElementById('chat_banner').setAttribute('onClick', `toggle_options('${data['group']}', '${data['group_name']}', 2)`);
                            document.getElementById('chatting_with_name').innerHTML = `${data['group_name']}`;
                        }
                        if(data['command'] == 'delete_group' && chat_type == '2' && chat_id == data['group']) {
                            purge_chat_area();
                        }
                    }
                }
                if(data['command'] == 'update_profile_pic') {
                    var messages_to_update = chat_area.querySelectorAll(`[user_id="${data['user']}"]`);
                    if (messages_to_update.length > 0) {
                        for(i = 0; i < messages_to_update.length; i++) {
                            messages_to_update[i].getElementsByTagName("IMG")[0].src = data['img_url'];
                        }
                    }
                }
                if(data['command'] == 'delete_user') {
                    if(chat_type == '1' && chat_id == `${data['deleted']}`) {
                        purge_chat_area();
                    }
                    if(chat_type == '2') {
                        var messages_to_delete = chat_area.querySelectorAll(`[user_id="${data['deleted']}"]`);
                        var counter = messages_to_delete.length; 
                        if (counter > 0) {
                            for(i = 0; i < counter; i++) {
                                messages_to_delete[i].parentNode.removeChild(messages_to_delete[i]);
                            }
                        }
                    }
                }
                if(data['command'] == 'user_removed_from_group') {
                    if(chat_type == '2' && chat_id == `${data['group']}`) {
                        if(data['users'][0] == user_id) {
                            purge_chat_area();
                        }
                    }
                }
            }
        }
    }
    catch(err){}
    finally{}
}

// Render Contact List
function render_contact_list() {
    fetch('render_contact_list')
    .then(response => response.json())
    .then(contact_list => {
        if(contact_list['logged_in']) {
            document.getElementById('friend_bar').innerHTML = '';
            var counter = contact_list['friend_ids'].length;
            var friend_column = '';
            var j = 0;
            for(i = 0; i < counter; i++) {
                let friend_row = `
                    <div class="contact" id="contact_${j}">
                        <div class="contact_friend_card" onclick="start_chat('${contact_list['friend_ids'][i]}', '${contact_list['friend_names'][i]}', 1)">
                            <img src="${contact_list['friend_imgs'][i]}" class="profile_pic_small">
                            <p class="contact_name">${contact_list['friend_names'][i]}</p>
                        </div>
                        <p id="group_add_${contact_list['friend_ids'][i]}" class="group_add" onclick="add_to_group('group_add_${contact_list['friend_ids'][i]}', '${contact_list['friend_names'][i]}')" onmouseover="show_group_add('group_add_${contact_list['friend_ids'][i]}')" onmouseout="hide_group_add('group_add_${contact_list['friend_ids'][i]}')">+</p>
                    </div>`;
                friend_column += friend_row;
                j++;
            }
            document.getElementById('friend_bar').insertAdjacentHTML('beforeend', friend_column);
            document.getElementById('group_bar').innerHTML = '';
            counter = contact_list['group_ids'].length;
            var group_column = '';
            for(i = 0; i < counter; i++) {
                let group_row = `
                    <div class="contact" id="contact_${j}" onclick="start_chat('${contact_list['group_ids'][i]}', '${contact_list['group_names'][i]}', 2)">
                        <img src="${contact_list['group_imgs'][i]}" class="profile_pic_small">
                        <p class="contact_name">${contact_list['group_names'][i]}</p>
                    </div>`;
                group_column += group_row;
                j++;
            }
            document.getElementById('group_bar').insertAdjacentHTML('beforeend', group_column);
        }
    });
}

async function get_default_group_image() {
    var url = '';
    await fetch('get_default_group_image')
    .then(response => response.json())
    .then(img => {
        url = img['url'];
    });
    return url;
}

async function add_to_group(contact_id, contact_name) {
    document.getElementById('overlay_title').innerHTML = 'Add to Group';
    document.getElementById('row_items').innerHTML='';
    var friend_id = contact_id.replace('group_add_', '');
    var content = '';
    var default_group_image = await get_default_group_image();
    var search_box = `
        <div class="overlay_content_row group_add_options" id="new_group">
            <div class="overlay_search_box"><input id="overlay_group_search_box" type="search" class="overlay_search_box" placeholder="Find Groups" onkeyup="search_groups(event)"></div>   `;
    content += search_box;
    var new_group = `
            <div onclick="new_group_form('${friend_id}')" class="new_group_link">
                <img src="${default_group_image}" class="profile_pic_small">
                <p class="new_group">Create New Group</p>
            </div>
        </div>
        <div class="break"></div>`;
    content += new_group;
    fetch(`add_group_list/${contact_id}`)
    .then(response => response.json())
    .then(groups => {
        var counter = groups['add_groups_ids'].length;
        for(row = 0; row < counter; row++){
            let result_row = `
                <div id="group_result_id_${groups['add_groups_ids'][row]}" class="overlay_content_row group_results" onclick="add_user_to_group('${groups['add_groups_ids'][row]}', '${contact_name}', '${friend_id}')" onmouseover="show_add_group('group_link_${groups['add_groups_ids'][row]}')" onmouseout="hide_add_group('group_link_${groups['add_groups_ids'][row]}')">
                    <img src="${groups['add_groups_imgs'][row]}" class="profile_pic_small">
                    <p class="contact_name">${groups['add_groups_names'][row]}</p>
                    <p class="add_group_link" id="group_link_${groups['add_groups_ids'][row]}">Add to Group <b>+</b></p>
                </div>`;
            content += result_row;
        }
        document.getElementById('row_items').insertAdjacentHTML('beforeend', content);
        document.getElementById('overlay').style.display = 'block';
    });
}

function show_add_group(group_link) {
    document.getElementById(group_link).style.display = 'flex';
}

function hide_add_group(group_link) {
    if(document.getElementById(group_link).innerHTML === 'Add to Group <b>+</b>'){
        document.getElementById(group_link).style.display = 'none';
    }
}

function add_user_to_group(group_id, friend_name, friend_id) {
    var group_link = `group_link_${group_id}`;
    if(!(document.getElementById(group_link).classList.contains('added_to_group_link'))) {
        fetch(`add_user_to_group/${friend_id}/${group_id}`)
        .then(response => response.json())
        .then(result => {
            if(result['success']) {
                document.getElementById(group_link).innerHTML = `Added ${friend_name} to group.`;
                document.getElementById(group_link).classList.add('added_to_group_link');
                update_group_list(group_id);
            }
        });
    }
}

async function new_group_url(contact) {
    var url = '';
    await fetch(`new_group_url/${contact}`)
    .then(response => response.json())
    .then(answer => {
        url = answer['url'];
    });
    return url;
}

async function new_group_form(contact) {
    document.getElementById('overlay_title').innerHTML = 'Create Group';
    var content = `
    <div id="new_group_error" class="error hidden">Group Name can't be empty</div>
    <form id="new_group_form" method="POST" enctype="multipart/form-data">
        <label>Group name</label>
        <input id="new_group_name" type="text" name="group_name" placeholder="Group name">
        <label>Group Image</label>
        <input id="img_upload" type="file" name="group_img" accept="image/*" onchange="image_upload()">
        <div class="register_img_upload" onclick="document.getElementById('img_upload_btn').click()"><label for="img_upload" id="img_upload_btn" class="register_img_text">Choose Image</label></div>
    </form>
        <button class="new_group_mask_button" onclick="create_new_group('${await new_group_url(contact)}')"><b>Create Group</b></button>`;
    document.getElementById('row_items').innerHTML=content;
}

function create_new_group(url) {
    var form = new FormData()
    var group_name = document.getElementById('new_group_name').value
    var group_pic = document.getElementById('img_upload').files
    form.append('group_name', group_name)
    form.append('group_img', group_pic[0])
    if(group_name != '') {
        fetch(url, {
            method: 'POST',
            body: form
        })
        .then(response => response.json())
        .then(executed => {
            if(executed['success']) {
                document.getElementById('overlay').style.display = 'none';
                document.getElementById('overlay_title').innerHTML = '';
                document.getElementById('row_items').innerHTML = '';
                update_group_list(executed['group_id'])
            }
            else {
                document.getElementById('overlay_title').innerHTML = 'Error while creating group';
                document.getElementById('row_items').innerHTML = '';
            }
        });
    }
    else {
        document.getElementById('new_group_error').classList.remove('hidden');
    }
}

function search_groups(event) {
    if(event.key != 'Escape') {
        var search_item = document.getElementById('overlay_group_search_box').value;
        var groups = document.getElementsByClassName('group_results');
        if(groups.length >= 1) {
            for(i = 0; i < groups.length; i++) {
                if(!(groups[i].getElementsByClassName('contact_name')[0].textContent.toUpperCase().includes(search_item.toUpperCase()))) {
                    groups[i].style.display = 'none';
                }
                else {
                    groups[i].style.display = 'flex';
                }
            }
        }
    }
    else {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('overlay_title').innerHTML = '';
        document.getElementById('row_items').innerHTML = '';
    }
}

function show_group_add(group_add_button) {
    document.getElementById(group_add_button).innerHTML='Add to Group';
}

function hide_group_add(group_add_button) {
    document.getElementById(group_add_button).innerHTML='+';
}

// Image upload
function image_upload() {
    let file_name = document.getElementById('img_upload').value;
    let start_strip = file_name.lastIndexOf('\\') + 1;
    document.getElementById('img_upload_btn').innerHTML = file_name.slice(start_strip);
    let label_text = document.getElementById('img_upload_btn').style;
    label_text.fontWeight = 'lighter';
}

// Loads user's notifications
async function show_notifications() {
    menu_click(document.getElementById('nav_menu'))
    document.getElementById('overlay_title').innerHTML = 'Notifications';
    document.getElementById('row_items').innerHTML='';
    // Get Notifications for user
    await fetch('load_notifications')
    .then(response => response.json())
    .then(async notifications => {
        if(notifications['counter'] === 0) {
            document.getElementById('row_items').insertAdjacentHTML('beforeend', `<div class="no_notif"><p>No notifications.</p></div>`);
        }
        else {
            var result_column = '';
            for(row = 0; row < notifications['counter']; row++) {
                switch(notifications['notif_type'][row]) {
                    case 0: // friend request
                        var result_row = `
                            <div id="friend_request_from_${notifications['var1'][row]}" class="overlay_content_row notif">
                                <p class="notif_text">You have a friend request from ${notifications['var2'][row]}!</p>
                                <button onclick="friend_request_response(${notifications['notified_user'][row]}, ${notifications['var1'][row]}, 1)" class="friend_accept_button">Accept</button>
                                <button onclick="friend_request_response(${notifications['notified_user'][row]}, ${notifications['var1'][row]}, 0)" class="friend_decline_button">Decline</button>
                            </div>`;
                        break;
                    case 1: // friend request accepted
                        var result_row = `
                            <div id="friend_request_accepted_${notifications['var1'][row]}" class="overlay_content_row notif">
                                <p class="notif_text notif_hover" onclick="remove_notification(1, '${notifications['notified_user'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">${notifications['var2'][row]} accepted your friend request!</p>
                                <button onclick="open_chat(1, 1, '${notifications['notified_user'][row]}', '${notifications['var2'][row]}', '${notifications['var1'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')" class="friend_accept_button">Open Chat</button>
                            </div>`;
                        break;
                    case 2: // friend request declined
                        var result_row = `
                            <div id="friend_request_declined_${notifications['var1'][row]}" class="overlay_content_row notif">
                                <p class="notif_text notif_hover" onclick="remove_notification(2, '${notifications['notified_user'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">${notifications['var2'][row]} declined your friend request!</p>
                            </div>`;
                        break;
                    case 3: // new message from friend
                        var username = await fetch(`get_username/${notifications['var1'][row]}`)
                        .then(response => response.json())
                        .then(username => {
                            return username['username'];
                        });
                        if(notifications['var2'][row] == '1') {
                            var message_type = 'a text message';
                        }
                        else if(notifications['var2'][row] == '2') {
                            var message_type = 'an image message';
                        }
                        var result_row = `
                            <div id="message_from_friend_${notifications['var1'][row]}" class="overlay_content_row notif">
                                <p class="notif_text notif_hover" onclick="open_chat(1, 3, '${notifications['notified_user'][row]}', '${username}', '${notifications['var1'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">${username} sent you ${message_type}.</p>
                            </div>`;
                        break;
                    case 4: // new message from group
                        var user_id = await fetch('get_user_id')
                        .then(response => response.json())
                        .then(result => {
                            return result['user_id'];
                        });
                        var groupname = await fetch(`get_groupname/${notifications['notified_group'][row]}`)
                        .then(response => response.json())
                        .then(groupname => {
                            return groupname['groupname'];
                        });
                        if(notifications['var2'][row] == '1') {
                            var message_type = 'A text message';
                        }
                        else if(notifications['var2'][row] == '2') {
                            var message_type = 'An image message';
                        }
                        if(user_id != notifications['var1'][row]) {
                            var result_row = `
                                <div id="message_from_group_${notifications['var1'][row]}" class="overlay_content_row notif">
                                    <p class="notif_text notif_hover" onclick="open_chat(2, 4, '${notifications['notified_group'][row]}', '${groupname}', '${notifications['notified_group'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">${message_type} was sent in the ${groupname} group.</p>
                                </div>`;
                        }
                        else if(user_id == notifications['var1'][row]) {
                            var result_row = '';
                        }
                        break;
                    case 5: // added to group
                        var result_row = `
                        <div id="added_to_group_${notifications['var1'][row]}" class="overlay_content_row notif">
                            <p class="notif_text notif_hover" onclick="open_chat(2, 5, '${notifications['notified_user'][row]}', '${notifications['var2'][row]}', '${notifications['var1'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">You were added to the ${notifications['var2'][row]} group.</p>
                        </div>`;
                        break;
                    case 6: // removed from group
                        var result_row = `
                        <div id="removed_from_group_${notifications['var1'][row]}" class="overlay_content_row notif">
                            <p class="notif_text notif_hover" onclick="remove_notification(6, '${notifications['notified_user'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">You were removed from the ${notifications['var2'][row]} group.</p>
                        </div>`;
                        break;
                    case 7: // removed from friends
                        var result_row = `
                        <div id="removed_friend_${notifications['var1'][row]}" class="overlay_content_row notif">
                            <p class="notif_text notif_hover" onclick="remove_notification(7, '${notifications['notified_user'][row]}', '${notifications['var1'][row]}', '${notifications['var2'][row]}')">You are no longer friends with ${notifications['var2'][row]}.</p>
                        </div>`;
                        break;
                }
                result_column += result_row;
            }
            document.getElementById('row_items').insertAdjacentHTML('beforeend', result_column);
        }
    });
    document.getElementById('overlay').style.display = 'block';
}

function remove_notification(notif_type, notif_user, var1, var2) {
    fetch(`remove_notification/${notif_type}/${notif_user}/${var1}/${var2}`)
    .then(response => response.json())
    .then(processed => {
        if(processed['removed']) {
            var row = null;
            switch(notif_type) {
                case 1:
                    row = document.getElementById(`friend_request_accepted_${var1}`);
                    break;
                case 2:
                    row = document.getElementById(`friend_request_declined_${var1}`);
                    break;
                case 6:
                    row = document.getElementById(`removed_from_group_${var1}`);
                    break;
                case 7:
                    row = document.getElementById(`removed_friend_${var1}`);
                    break;
            }
            row.classList.toggle('notif_clicked');
            setTimeout(function k(){
                row.classList.add('notif_remove');
                setTimeout(function m(){
                    row.parentNode.removeChild(row);
                }, 400);
            }, 400);
        }
        else {
            alert('An error occurred!')
        }
    });
}

function open_chat(chat_type, notif_type, notif_user, chat_name, chat_id, var1, var2) {
    togle_empty_chat_overlay(1);
    start_chat(chat_id, chat_name, chat_type);
    fetch(`remove_notification/${notif_type}/${notif_user}/${var1}/${var2}`)
    .then(response => response.json())
    .then(processed => {
        if(processed['removed']) {
            close_overlay();
        }
    });
}

// Respond to Friend Request & remove notification
function friend_request_response(user_id, sender_id, option) {
    fetch(`friend_request_response/${user_id}/${sender_id}/${option}`)
    .then(response => response.json())
    .then(processed => {
        if(processed['processed']) {
            var row = document.getElementById(`friend_request_from_${sender_id}`);
            row.classList.toggle('notif_clicked');
            setTimeout(function l(){
                switch(option){
                    case 0: // Decline request
                        row.innerHTML = `<p class="notif_text">You have declined ${processed["sender"]}'s friend request!</p>`;
                        break;
                    case 1: // Accept request
                        row.innerHTML = `<p class="notif_text">You have accepted ${processed["sender"]}'s friend request!</p>`;
                        update_friend_list(user_id, sender_id);
                        break;
                }
                row.classList.toggle('notif_clicked');
            }, 400);
            setTimeout(function l(){
                row.classList.toggle('notif_clicked');
                setTimeout(function k(){
                    row.classList.add('notif_remove');
                    setTimeout(function m(){
                        try{
                            row.parentNode.removeChild(row);
                        }
                        catch(error){}
                        finally{}
                    }, 400);
                }, 400);
            }, 3000);
        }
    });
}

async function show_account_settings() {
    menu_click(document.getElementById('nav_menu'))
    var user_id = null;
    await fetch('get_user_id')
    .then(response => response.json())
    .then(result => {
        user_id = result['user_id'];
    });
    document.getElementById('overlay_title').innerHTML = 'Account Settings';
    document.getElementById('row_items').innerHTML=`
        <p onclick="delete_user(${user_id})" class="options_text_red">Delete Account</p>
        <p onclick="change_profile_pic(${user_id})" class="options_text_green">Change Profile Picture</p>`;
    document.getElementById('overlay').style.display = 'block';
}

function change_profile_pic() {
    document.getElementById('overlay_title').innerHTML = 'Change Profile Image';
    var content = `
    <form id="new_group_form" method="POST" enctype="multipart/form-data">
        <label>New Profile Image</label>
        <input id="img_upload" type="file" name="profile_img" accept="image/*" onchange="image_upload()">
        <div class="register_img_upload" onclick="document.getElementById('img_upload_btn').click()"><label for="img_upload" id="img_upload_btn" class="register_img_text">Choose Image</label></div>
    </form>
        <button class="new_group_mask_button" onclick="change_profile_pic_commit()"><b>Upload Image</b></button>`;
    document.getElementById('row_items').innerHTML=content;
}

function change_profile_pic_commit() {
    var form = new FormData();
    var profile_pic = document.getElementById('img_upload').files;
    form.append('profile_pic', profile_pic[0]);
    fetch('profile_pic_change', {
        method: 'POST',
        body: form
    })
    .then(response => response.json())
    .then(executed => {
        if(executed['success']) {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('overlay_title').innerHTML = '';
            document.getElementById('row_items').innerHTML = '';
            update_profile_pic(executed['user_id'], executed['img_url'])
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'Error while changing profile image!';
            document.getElementById('row_items').innerHTML = '';
        }
    });
}

// Search function
function search(event) {
    var search_item = document.getElementById('search_text').value;
    var contacts = document.getElementsByClassName('contact');
    if(event.key === 'Enter') {
        // Code for global search
        // Show all Contacts/Groups
        if(contacts.length > 0) {
            for(i = 0; i < contacts.length; i++) {
                document.getElementById(`contact_${i}`).style.display = 'flex';
            }
        }
        // API search:
        if(search_item != ''){
            fetch(`search_engine/${search_item}`)
            .then(response => response.json())
            .then(search_results => {
                if(search_results['counter'] === 0){
                    document.getElementById('overlay_title').innerHTML = `No results found for: ${search_item}`;
                }
                if(search_results['counter'] === 1){
                    document.getElementById('overlay_title').innerHTML = `One result found for: ${search_item}`;
                }
                if(search_results['counter'] > 1){
                    document.getElementById('overlay_title').innerHTML = `Top ${search_results['counter']} results for: ${search_item}`;
                }
                var result_column = '';
                for(row = 0; row < search_results['counter']; row++){
                    if(search_results["request_sent"][row]) {
                        var add_remove = `Cancel Request<b>-</b>`;
                        var onclick_function = `remove_friend_request(${search_results['user_id'][row]})`;
                    }
                    else {
                        var add_remove = `Add Friend<b>+</b>`;
                        var onclick_function = `add_friend(${search_results['user_id'][row]})`;
                    }
                    let result_row = `
                        <div id="search_result_id_${search_results['user_id'][row]}" class="overlay_content_row" onclick="` + onclick_function + `" onmouseover="show_add_friend('friend_link_${search_results['user_id'][row]}')" onmouseout="hide_add_friend('friend_link_${search_results['user_id'][row]}')">
                            <img src="${search_results['results_pics'][row]}" class="profile_pic_small">
                            <p class="contact_name">${search_results['results_names'][row]}</p>
                            <p class="add_friend_link" id="friend_link_${search_results['user_id'][row]}">`+ add_remove +`</p>
                        </div>
                    `;
                    result_column += result_row;
                }
                document.getElementById('row_items').innerHTML = result_column;
                document.getElementById('overlay').style.display = 'block';
            });
        }
        else{
            document.getElementById('overlay_title').innerHTML = 'Error: Search box is empty!';
            document.getElementById('row_items').innerHTML='';
            document.getElementById('overlay').style.display = 'block';
        }
    }
    // Code for existing friend/group search
    else if (!(document.getElementById('overlay').style.display === 'block')) {
        if(contacts.length >= 1) {
            for(i = 0; i < contacts.length; i++) {
                if(!(contacts[i].textContent.toUpperCase().includes(search_item.toUpperCase()))) {
                    document.getElementById(`contact_${i}`).style.display = 'none';
                }
                else {
                    document.getElementById(`contact_${i}`).style.display = 'flex';
                }
            }
        }
    }
}

// Close overlay
function close_overlay() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('overlay_title').innerHTML = '';
    document.getElementById('row_items').innerHTML = '';
    document.getElementById('search_text').value = '';
}

function show_add_friend(x) {
    document.getElementById(x).style.display = 'flex';
}

function hide_add_friend(x) {
    document.getElementById(x).style.display = 'none';
}

// Send friend request
function add_friend(user_id) {
    fetch(`add_friend/${user_id}`)
    .then(response => response.json())
    .then(send_friend_request => {
        if(send_friend_request['created']) {
            document.getElementById(`friend_link_${user_id}`).innerHTML = "Cancel Request<b>-</b>";
            document.getElementById(`search_result_id_${user_id}`).setAttribute('onClick', `remove_friend_request(${user_id})`);
        }
    });
}

// Revoke friend request
function remove_friend_request(user_id) {
    fetch(`remove_friend_request/${user_id}`)
    .then(response => response.json())
    .then(remove_request => {
        if(remove_request['removed']) {
            document.getElementById(`friend_link_${user_id}`).innerHTML = "Add Friend<b>+</b>";
            document.getElementById(`search_result_id_${user_id}`).setAttribute('onClick', `add_friend(${user_id})`);
        }
    });
}

async function end_friendship(friend_id, friend_name) {
    var user_id = null;
    await fetch('get_user_id')
    .then(response => response.json())
    .then(result => {
        user_id = result['user_id'];
    });
    fetch(`remove_friend/${friend_id}`)
    .then(response => response.json())
    .then(executed => {
        if(executed['success']) {
            update_friend_list(user_id, friend_id);
        }
        else if(!executed['success']) {
            alert(`An error occured while removing ${friend_name} from your contact list`)
        }
    });
    close_overlay();
}

async function toggle_options(chat_id, chat_name, type) {
    // type 1 => chat id = friend id
    // type 2 => chat id = groupchat id
    switch(type) {
        case 1:
            document.getElementById('overlay_title').innerHTML = `Contact options for: ${chat_name}`;
            document.getElementById('row_items').innerHTML = `
                <p class="options_text_red" onclick="end_friendship('${chat_id}', '${chat_name}')">End Friendship</p>`;
            break;
        case 2:
            document.getElementById('overlay_title').innerHTML = `Group Chat settings for: ${chat_name}`;
            var settings = '';
            var exit = `<p class="options_text_red" onclick="exit_group('${chat_id}')">Exit Group</p>`;
            var user_privilege = null;
            await fetch(`get_user_privilege/${chat_id}`)
            .then(response => response.json())
            .then(result => {
                user_privilege = result['user_privilege'];
            });
            if(user_privilege >= 1) {
                settings += `
                    <p class="options_text_green" onclick="add_new_user('${chat_id}', '${chat_name}')">Add Friend to Group</p>
                    <p class="options_text_red" onclick="remove_user('${chat_id}', '${chat_name}')">Remove User from Group</p>`;
            }
            if(user_privilege == 2) {
                settings += `
                    <p class="options_text_green" onclick="change_privilege_lvl('${chat_id}')">Change Members' privilege levels</p>
                    <p class="options_text_green" onclick="change_group_name('${chat_id}', '${chat_name}')">Change Group Name</p>
                    <p class="options_text_green" onclick="change_group_icon('${chat_id}')">Change Group Icon</p>
                    <p class="options_text_red" onclick="delete_group('${chat_id}')">Delete Group</p>
                `;
            }
            settings += exit;
            document.getElementById('row_items').innerHTML = settings;
            break;
    }
    document.getElementById('overlay').style.display = 'block';
}

function add_to_this_group(friend_id, group_id) {
    fetch(`add_user_to_group/${friend_id}/${group_id}`)
    .then(response => response.json())
    .then(answer => {
        if(answer['success']) {
            close_overlay();
            update_group_list(group_id);
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'ERROR';
            document.getElementById('row_items').innerHTML = 'An error occurred while adding user to group';
        }
    });
}

function add_new_user(group_id, group_name) {
    document.getElementById('overlay_title').innerHTML = `Add friend to: ${group_name}`;
    document.getElementById('row_items').innerHTML = ``;
    fetch(`get_friend_list/${group_id}`)
    .then(response => response.json())
    .then(friends => {
        var counter = friends['friend_ids'].length;
        var friend_list = '';
        if(counter > 0) {
            for(i = 0; i < counter; i++) {
                let friend_row = `
                    <div class="contact_friend_card contact_hover" onclick="add_to_this_group('${friends['friend_ids'][i]}', '${group_id}')">
                        <img src="${friends['friend_imgs'][i]}" class="profile_pic_small">
                        <p class="contact_name">${friends['friend_names'][i]}</p>
                    </div>`;
                    friend_list += friend_row;
            }
            document.getElementById('row_items').innerHTML = friend_list;
        }
        else {
            document.getElementById('row_items').innerHTML = '<p class="options_text">There are no friends you can add!</p>';
        }
    });
}

function remove_from_this_group(user_id, group_id) {
    fetch(`remove_from_group/${user_id}/${group_id}`)
    .then(response => response.json())
    .then(answer => {
        if(answer['success']) {
            close_overlay();
            user_removed_from_group(user_id, group_id);
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'ERROR';
            document.getElementById('row_items').innerHTML = 'An error occurred while removing user from group';
        }
    });
}

function remove_user(group_id, group_name) {
    document.getElementById('overlay_title').innerHTML = `Remove user from: ${group_name}`;
    document.getElementById('row_items').innerHTML = ``;
    fetch(`get_member_list/${group_id}`)
    .then(response => response.json())
    .then(users => {
        var counter = users['member_ids'].length;
        var user_list = '';
        if(counter > 0) {
            for(i = 0; i < counter; i++) {
                let user_row = `
                    <div class="contact_friend_card contact_hover_red" onclick="remove_from_this_group('${users['member_ids'][i]}', '${group_id}')">
                        <img src="${users['member_imgs'][i]}" class="profile_pic_small">
                        <p class="contact_name">${users['member_names'][i]}</p>
                    </div>`;
                    user_list += user_row;
            }
            document.getElementById('row_items').innerHTML = user_list;
        }
        else {
            document.getElementById('row_items').innerHTML = '<p class="options_text">There are no users you can remove!</p>';
        }
    });
}

function change_privilege(user_id, group_id, option) {
    fetch(`change_privilege/${user_id}/${group_id}/${option}`)
    .then(response => response.json())
    .then(answer => {
        if(answer['success']) {
            close_overlay();
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'ERROR';
            document.getElementById('row_items').innerHTML = 'An error occurred while changing the privilege level!';
        }
    });
}

function change_privilege_lvl(group_id) {
    document.getElementById('overlay_title').innerHTML = 'Change group permissions for users';
    document.getElementById('row_items').innerHTML = ``;
    fetch(`get_member_list/${group_id}`)
    .then(response => response.json())
    .then(users => {
        var counter = users['member_ids'].length;
        var user_list = '';
        if(counter > 0) {
            for(i = 0; i < counter; i++) {
                var standard = `<p class="options_text_red align_right" onclick="change_privilege(${users['member_ids'][i]}, ${group_id}, '0')">Standard</p>`;
                var admin = `<p class="options_text_green" onclick="change_privilege(${users['member_ids'][i]}, ${group_id}, '2')">Admin</p>`;
                let user_row = `
                    <div class="contact_friend_card">
                        <img src="${users['member_imgs'][i]}" class="profile_pic_small">
                        <p class="contact_name">${users['member_names'][i]}</p>`
                if(users['member_privilege'][i] == 0) {
                    let mod = `<p class="options_text_green align_right" onclick="change_privilege(${users['member_ids'][i]}, ${group_id}, '1')">Moderator</p>`;
                    user_row += mod;
                    user_row += admin;
                }
                else if(users['member_privilege'][i] == 1) {
                    user_row += standard;
                    user_row += admin;
                }
                else if(users['member_privilege'][i] == 2) {
                    let mod = `<p class="options_text_red" onclick="change_privilege(${users['member_ids'][i]}, ${group_id}, '1')">Moderator</p>`;
                    user_row += standard;
                    user_row += mod;
                }
                user_row += `</div>`;
                    user_list += user_row;
            }
            document.getElementById('row_items').innerHTML = user_list;
        }
        else {
            document.getElementById('row_items').innerHTML = '<p class="options_text">There are no users you can change the privilege of!</p>';
        }
    });
}

async function change_group_name(group_id, group_name) {
    document.getElementById('overlay_title').innerHTML = 'Change group Name';
    var content = `
    <div id="new_group_error" class="error hidden">Group Name can't be empty</div>
    <form id="group_name_form" method="POST">
        <label>Group name</label>
        <input id="new_group_name" type="text" name="group_name" placeholder="${group_name}">
    </form>
        <button class="new_group_mask_button" onclick="change_group_name_commit('${group_id}')"><b>Change name</b></button>`;
    document.getElementById('row_items').innerHTML=content;
}

function change_group_name_commit(group_id) {
    var form = new FormData();
    var group_name = document.getElementById('new_group_name').value;
    form.append('group_name', group_name);
    if(group_name != '') {
        fetch(`group_change_name/${group_id}`, {
            method: 'POST',
            body: form
        })
        .then(response => response.json())
        .then(executed => {
            if(executed['success']) {
                document.getElementById('overlay').style.display = 'none';
                document.getElementById('overlay_title').innerHTML = '';
                document.getElementById('row_items').innerHTML = '';
                refresh_group_list(group_id);
                reload_banner(group_id, group_name);
            }
            else {
                document.getElementById('overlay_title').innerHTML = 'Error while renaming group!';
                document.getElementById('row_items').innerHTML = '';
            }
        });
    }
    else {
        document.getElementById('new_group_error').classList.remove('hidden');
    }
}

function change_group_icon(group_id) {
    document.getElementById('overlay_title').innerHTML = 'Change group icon';
    var content = `
    <form id="new_group_form" method="POST" enctype="multipart/form-data">
        <label>New Group Icon</label>
        <input id="img_upload" type="file" name="group_img" accept="image/*" onchange="image_upload()">
        <div class="register_img_upload" onclick="document.getElementById('img_upload_btn').click()"><label for="img_upload" id="img_upload_btn" class="register_img_text">Choose Image</label></div>
    </form>
        <button class="new_group_mask_button" onclick="change_group_icon_commit('${group_id}')"><b>Change Icon</b></button>`;
    document.getElementById('row_items').innerHTML=content;
}

function change_group_icon_commit(group_id) {
    var form = new FormData();
    var group_img = document.getElementById('img_upload').files;
    form.append('group_img', group_img[0]);
    fetch(`group_change_img/${group_id}`, {
        method: 'POST',
        body: form
    })
    .then(response => response.json())
    .then(executed => {
        if(executed['success']) {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('overlay_title').innerHTML = '';
            document.getElementById('row_items').innerHTML = '';
            refresh_group_list(group_id)
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'Error while changing group icon!';
            document.getElementById('row_items').innerHTML = '';
        }
    });
}

function exit_group(group_id) {
    fetch(`exit_group/${group_id}`)
    .then(response => response.json())
    .then(processed => {
        if(processed['success']) {
            render_contact_list();
            if(processed['delete']) {
                delete_group(group_id);
            }
        }
        else {
            alert('An error occurred while exiting the group');
        }
        close_overlay();
        purge_chat_area()
    })
}

// Code for Django Channels & sockets
function close_chat_sockets() {
    try{
        ChatSocket.close();
    }
    catch(error){}
    finally{}
}

function load_initial_messages(){
    ChatSocket.send(JSON.stringify({
        'timestamp': 0,
        'command': 'fetch_previous_messages'
    }));
}

async function get_Friend_Chat_room(link_id) {
    var friend_chat_room = '';
    await fetch(`get_Friend_Chat_Ledger/${link_id}`)
    .then(response => response.json())
    .then(chat_room => {
        if(chat_room['success']) {
            friend_chat_room = chat_room['friend_chat_id'];
        }
        else {
            friend_chat_room = false;
        }
    });
    return friend_chat_room;
}

function start_send_chat_image(link_id, type) {
    send_img_form(link_id, type);
    document.getElementById('overlay').style.display = 'block';
}

function make_chat_notification(message_type) {
    var chat_type = chat_container.getAttribute('chat_type');
    var chat_id = chat_container.getAttribute('chat_id');
    fetch(`make_chat_notification/${chat_id}/${chat_type}/${message_type}`)
    .then(response => response.json())
    .then(processed => {
        if(!processed['success']) {
            alert('An error occurred!')
        }
    });
}

function send_text_message() {
    const text_message_to_send = text_message_content.value;
    text_message_content.value = '';
    make_chat_notification(1);
    ChatSocket.send(JSON.stringify({
        'message': text_message_to_send,
        'command': 'send_new_text_message'
    }));
}

async function send_img_to_chat_message(img_url) {
    make_chat_notification(2);
    ChatSocket.send(JSON.stringify({
        'message': img_url,
        'command': 'send_new_img_message'
    }));
}

async function send_img_form(link_id, type) {
    document.getElementById('overlay_title').innerHTML = 'Upload Image';
    var chat_room = null;
    switch(type){
        case 1:
            chat_room = await get_Friend_Chat_room(link_id);
            break;
        case 2:
            chat_room = link_id;
            break;
    }
    var content = `
        <form id="send_img_form" method="POST" enctype="multipart/form-data">
            <label>Image to send</label>
            <input id="img_upload" type="file" name="send_chat_img" accept="image/*" onchange="image_upload()">
            <div class="register_img_upload" onclick="document.getElementById('img_upload_btn').click()"><label for="img_upload" id="img_upload_btn" class="register_img_text">Choose Image</label></div>
        </form>
            <button class="send_img_mask_button" onclick="send_image('${chat_room}', '${type}')"><b>Send</b></button>`;
    document.getElementById('row_items').innerHTML=content;
}

async function send_image(chat_ledger, type) {
    var form = new FormData()
    var image_to_send = document.getElementById('img_upload').files
    form.append('image_to_send', image_to_send[0])
    fetch(`chat_img_upload/${chat_ledger}/${type}`, {
        method: 'POST',
        body: form
    })
    .then(response => response.json())
    .then(executed => {
        if(executed['success']) {
            send_img_to_chat_message(executed['img_url']);
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('overlay_title').innerHTML = '';
            document.getElementById('row_items').innerHTML = '';
        }
        else {
            document.getElementById('overlay_title').innerHTML = 'Error while uploading image!';
            document.getElementById('row_items').innerHTML = '';
        }
    });
}

async function start_chat(link_id, chat_name, type) {
    togle_empty_chat_overlay(1);
    if(window_width <= 800) {
        max_chat()
    }
    close_chat_sockets();
    document.getElementById('chat_banner').setAttribute('onClick', `toggle_options(${link_id}, '${chat_name}', ${type})`);
    chat_banner.innerHTML = chat_name;
    chat_area.innerHTML = '';
    // type 1 = friend chat
    // type 2 = group chat
    var friend_chat_ledger = null;
    var socket_link = null;
    var user_id = null;
    switch(type) {
        case 1:
            friend_chat_ledger = await get_Friend_Chat_room(link_id);
            if(friend_chat_ledger){
                socket_link = 'ws://' + window.location.host + '/ws/chat/' + friend_chat_ledger + '/' + type + '/';
            }
            break;
        case 2:
            socket_link = 'ws://' + window.location.host + '/ws/chat/' + link_id + '/' + type + '/';
            break;
    }
    await fetch('get_user_id')
    .then(response => response.json())
    .then(result => {
        user_id = result['user_id'];
    });
    ChatSocket = new WebSocket(socket_link);
    ChatSocket.onopen = function() {
        load_initial_messages();
    }
    ChatSocket.onmessage = async function(e) {
        const data = JSON.parse(e.data);
        if(data['command'].includes('previous_messages')){
            if(data['messages'] != 'done') {
                var message_list = [];
                for(var i in data['messages']) {
                    //load messages
                    var div_class = '';
                    if (data['messages'][i]['owner'] == user_id) {
                        div_class = 'user_message';
                    }
                    else {
                        div_class = 'friend_message';
                    }
                    if(data['command'] == 'initial_previous_messages'){
                        div_class += ' hidden_message';
                    }
                    switch(type) {
                        case 1:
                            var message_type = '';
                            break;
                        case 2:
                            var img = '';
                            if(data['messages'][i]['message_type'] == 'image') {
                                img = 'pic_message';
                            }
                            if(data['messages'][i]['owner'] != user_id) {
                                var message_type = `<div class="group_friend_message ` + img + `"><div><p><i>${data['messages'][i]['owner_name']}</i></p></div>`;
                            }
                            else {
                                var message_type = '';
                            }
                            break;
                    }
                    if(data['messages'][i]['message_type'] == 'text') {
                        message_type += `<p>${data['messages'][i]['text']}</p>`;
                    }
                    else {
                        message_type += `<img class="img_message" src="${data['messages'][i]['img']}">`;
                    }
                    if(type == 2) {
                        message_type += '</div>';
                    }
                    var message = `
                        <div class="${div_class}" timestamp="${data['messages'][i]['timestamp']}" user_id="${data['messages'][i]['owner']}">
                            <div class="chat_profile_pic">
                                <img src="${data['messages'][i]['profile_pic']}" class="profile_pic_small">
                            </div>` +
                            message_type +
                        `</div>`;
                    message_list.push(message);
                }
                for(i = 0; i < message_list.length; i++) {
                    chat_area.insertAdjacentHTML('afterbegin', message_list[i]);
                }
            }
            if(data['messages'] == 'done') {
                var done = `
                    <div class="end_of_messages">Start of chat.</div>
                `; 
                chat_area.insertAdjacentHTML('afterbegin', done);
            }
            if(data['command'] == 'initial_previous_messages') {
                scroll_bottom(true);
            }
        }
        if(data['command'] == 'send_new_text_message'){
            if(data['chat_type'] == 1) {
                var notif_type = 3;
            }
            else if(data['chat_type'] == 2) {
                var notif_type = 4;
            }
            var notif_user = await fetch('get_user_id')
            .then(response => response.json())
            .then(result => {
                return result['user_id'];
            });
            var chat_id = chat_container.getAttribute('chat_id');
            if(notif_type == 3) {
                fetch(`remove_notification/${notif_type}/${notif_user}/${chat_id}/1`);
            }
            else if(notif_type == 4) {
                fetch(`remove_notification/${notif_type}/${chat_id}/${data['message']['owner']}/1`);
            }
            var div_class = '';
            if (data['message']['owner'] == user_id) {
                div_class = 'user_message';
            }
            else {
                div_class = 'friend_message';
            }
            switch(type) {
                case 1:
                    var message_type = '';
                    break;
                case 2:
                    if(data['message']['owner'] != user_id) {
                        var message_type = `<div class="group_friend_message"><div><p><i>${data['message']['owner_name']}</i></p></div>`;
                    }
                    else {
                        var message_type = '';
                    }
                    break;
            }
            var message = `
                <div class="${div_class}" timestamp="${data['message']['timestamp']}" user_id="${data['message']['owner']}">
                    <div class="chat_profile_pic">
                        <img src="${data['message']['profile_pic']}" class="profile_pic_small">
                    </div>` +
                    message_type +
                    `<p>${data['message']['text']}</p>
                </div>
            `;
            chat_area.insertAdjacentHTML('beforeend', message);
            if(div_class == 'user_message'){
                scroll_bottom(false);
            }
            bottom_magnet()
        }
        if(data['command'] == 'send_new_img_message'){
            if(data['chat_type'] == 1) {
                var notif_type = 3;
            }
            else if(data['chat_type'] == 2) {
                var notif_type = 4;
            }
            var notif_user = await fetch('get_user_id')
            .then(response => response.json())
            .then(result => {
                return result['user_id'];
            });
            var chat_id = chat_container.getAttribute('chat_id');
            if(notif_type == 3) {
                fetch(`remove_notification/${notif_type}/${notif_user}/${chat_id}/2`);
            }
            else if(notif_type == 4) {
                fetch(`remove_notification/${notif_type}/${chat_id}/${data['message']['owner']}/2`);
            }
            var div_class = '';
            if (data['message']['owner'] == user_id) {
                div_class = 'user_message';
            }
            else {
                div_class = 'friend_message';
            }
            switch(type) {
                case 1:
                    var message_type = '';
                    break;
                case 2:
                    if(data['message']['owner'] != user_id) {
                        var message_type = `<div class="group_friend_message pic_message"><div><p><i>${data['message']['owner_name']}</i></p></div>`;
                    }
                    else {
                        var message_type = '';
                    }
                    break;
            }
            var message = `
                <div class="${div_class}" timestamp="${data['message']['timestamp']}" user_id="${data['message']['owner']}">
                    <div class="chat_profile_pic">
                        <img src="${data['message']['profile_pic']}" class="profile_pic_small">
                    </div>` +
                    message_type +
                    `<img class="img_message" src="${data['message']['img']}">
                </div>`;
            chat_area.insertAdjacentHTML('beforeend', message);
            if(div_class == 'user_message'){
                scroll_bottom(false);
            }
            bottom_magnet()
        }
    };
    send_message.setAttribute('onClick', `send_text_message()`);
    send_img_message.setAttribute('onClick', `start_send_chat_image(${link_id}, ${type})`);
    chat_container.setAttribute('chat_type', `${type}`);
    chat_container.setAttribute('chat_id', `${link_id}`);
}