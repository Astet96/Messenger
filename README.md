My project is at it's core a real time messenger app, much like WhatsApp and Discord in functionality and appearance.
The app fully supports sending and receiving image files, as well as automatic file system management of said files.
The app supports 1-to-1 and group chats, with admin and moderator settings available for the later.
In order to facilitate instant messaging I implemented websockets via the Django Channels plugin for Python.
This package is configured to run with Redis server out of the box. As such I installed Redis on the latest version of Ubuntu running on
the Linux subsystem for Windows 10.

Overall, the application features all the standard functionality one would expect from a modern messenger service, including a notifications system.
In making the app I did not use any third party javascript frameworks or css, the entirety of the code being written by me.

There are three main reasons for which I've chosen to embark on such a complex project. First of all to take on the challenge of a complex design, and learn
from first-hand experience the issues that one has to consider when working on more advanced projects. Moreover, there is the desire to learn, which led me to
attempt and implement websockets as both a learning experience and personal challenge. Finally, I believe that such a project will be instrumental in achieving
my long term goals for a career in programming. Considering the above, I can confidently state that the application fully meets and possibly
exceeds the expected distinctiveness and complexity requirements.

views.py:
includes the basic functions for registering, login & logout
this app can be viewed as a one page application since once logged in, the index page the only one that the
user will be inside. As such there are many API paths, called through javascript, which relate to view functions

models.py:
The models used represent users, friendships (which double as 1-on-1 chat ledger identifiers), chat logs, groups
and notifications
A simplified DB schema png file is available to better show these relationships

consumers.py:
This file contains the two socket consumers required. The first one is responsible for chat functionality.
The second one is responsible for the real time render of the contact and group list.
In building these consumers I have used extensively the methods that are showcased in the following tutorials:
https://channels.readthedocs.io/en/latest/
https://www.youtube.com/watch?v=Wv5jlmJs2sU
https://www.youtube.com/watch?v=xrKKRRC518Y

scripts.js:
This file contains all the scripting required for the app to work, and was written by myself without the use of
third party frameworks. There are three areas where javascript is used:
1. basic animations and website design
2. communication between the back-end and front-end via fetch requests on API functions in the views.py file
3. websocket communication via the two sockets and their methods described in the consumers.py file

styles.css:
This file contains all the styling for the web app. All of the code was written by me, unless stated otherwise
inside the file. To achieve certain effects and animations I have adapted code from w3schools and stackoverflow
question threads. All credit is given inside the css file as commented text.
# Messenger
