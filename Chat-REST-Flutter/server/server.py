from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque
from markupsafe import escape

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# The class to represent a room
class Room:
    def __init__(self, room_name):
        self.room_name = room_name
        # Current users joined the room
        self.users = []
        # Current messages in the room
        self.messages = []

    # get the name of the room
    def get_name(self):
        return self.room_name

    # set the name of the room
    def set_name(self, room_name):
        self.room_name = room_name

    # Join a new user to the room
    def add_user(self, user):
        if not self.has_user(user):
            self.users.append(user)
            return True
        return False

    # Check if user has joined this room
    def has_user(self, user):
        return user in self.users

    # Remove a user from this room
    def remove_user(self, user):
        if self.has_user(user):
            self.users.remove(user)
            return True
        return False

    # Add a new message to this room
    def add_message(self, user, msg):
        if self.has_user(user):
            self.messages.append(Message(user, msg))
            return True
        return False


    # Get all the messages of this room
    def get_messages(self):
        return self.messages

# Class representing a user
class User:
    def __init__(self, user_name):
        # The name of the user
        self.user_name = user_name
        # The rooms this user has joined
        self.rooms = []

    # Join a room
    def join_room(self, room):
        if room not in self.rooms:
            self.rooms.append(room)
            return True
        return False

    # Leave a room
    def leave_room(self, room):
        if room in self.rooms:
            self.rooms.remove(room)
            return True
        return False

    def get_user_name(self):
        return self.user_name

    # Check if user can send message to this room
    def can_send(self, room):
        return room in self.rooms


class Message:
    def __init__(self, user, msg):
        self.user = user
        self.msg = msg

    def get_message(self):
        return self.msg

    def get_user(self):
        return self.user



# All the rooms
rooms = []
# All the users
users = []

# Search if a room exists and return it
def search_room(room_name):
    for r in rooms:
        if r.room_name == room_name:
            return r
    return None

# search if a user exists and return it
def search_user(user_name):
    for u in users:
        if u.user_name == user_name:
            return u
    return None

@app.route("/create-room", methods=["POST"])
def create_room():
    data = request.json
    room_name = data.get('room-name')
    if not room_name:
        return jsonify({"error": "room-name is required to create a new room"}), 400
    if search_room(room_name) == None:
        rooms.append(Room(room_name))
        print("> Room " + room_name + " created.")
        return jsonify({"success": f"Room {room_name} created"}), 200
    print(f"* Cannot create room {room_name}.")
    return jsonify({"error": f"Cannot create {room_name}"}), 400


# Remove a room
@app.route("/remove-room", methods=["POST"])
def remove_room():
    data = request.json
    room_name = data.get('room-name')
    if not room_name:
        return jsonify({"error": "room-name is required to remove a room"}), 400
    to_remove = search_room(room_name)
    if to_remove != None:
        rooms.remove(to_remove)
        print(f"> Room {room_name} removed.")
        return jsonify({"success": f"Room {room_name} removed"}), 200
    print(f"* Cannot reamove room {room_name}.")
    return jsonify({"error": f"Cannot remove {room_name}"}), 400

# Get all the rooms
@app.route("/get-rooms", methods=["POST"])
def get_rooms():
    data = request.json
    user_name = data.get('user-name')
    if not user_name:
        return jsonify({"error": "user-name is required to get all the room"}), 400
    user = search_user(user_name)
    rooms_list = ''
    for room in rooms:
        rooms_list += '\t' + room.get_name()
        if(room.has_user(user)):
            rooms_list += ' [joined]'
        rooms_list += '\n'
    print(f"> Listing the rooms for client {user.user_name}")
    return jsonify({"success": rooms_list}), 200

# Add a new user
@app.route("/add-user", methods=["POST"])
def add_user():
    data = request.json
    user_name = data.get('user-name')
    if not user_name:
        return jsonify({"error": "user-name is required to add user"}), 400
    if search_user(user_name) == None:
        users.append(User(user_name))
        print(f"> User {user_name} was added.")
        return jsonify({"success": f"User {user_name} was added"}), 200
    print(f"* Cannot add user {user_name}.")
    return jsonify({"error": f"Cannot add user {user_name}"}), 400

# # Remove a user
@app.route("/remove-user", methods=["POST"])
def remove_user():
    data = request.json
    user_name = data.get('user-name')
    if not user_name:
        return jsonify({"error": "user-name is required to remove user"}), 400
    to_remove = search_user(user_name)
    if to_remove != None:
        users.remove(to_remove)
        for r in rooms:
            r.remove_user(to_remove)
        print(f"> User {user_name} was removed.")
        return jsonify({"success": f"User {user_name} was removed"}), 200
    print(f"* Cannot remove user {user_name}.")
    return jsonify({"error": f"Cannot remove user {user_name}"}), 400

# join a room
@app.route("/join-room", methods=["POST"])
def join_room():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to join room"}), 400

    user = search_user(user_name)
    room = search_room(room_name)
    if user == None or room == None:
        print(f"* User {user_name} cannot join {room_name}")
        return jsonify({"error": f"User {user_name} cannot join {room_name}"}), 400
    result = user.join_room(room) and room.add_user(user)
    if result == True:
        print(f"> User {user_name} joined {room_name}")
        return jsonify({"success": f"User {user_name} joined {room_name}"}), 200
    else:
        print(f"* User {user_name} cannot join {room_name}")
        return jsonify({"error": f"User {user_name} cannot join {room_name}"}), 400

# # Leave a room
@app.route("/leave-room", methods=["POST"])
def leave_room():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to leave room"}), 400

    user = search_user(user_name)
    room = search_room(room_name)
    if user == None or room == None:
        print(f"* User {user_name} cannot leave {room_name}")
        return jsonify({"error": f"User {user_name} cannot leave {room_name}"}), 400
    result = user.leave_room(room) and room.remove_user(user)
    if result == True:
        print(f"> User {user_name} left {room_name}")
        return jsonify({"success": f"User {user_name} left {room_name}"}), 200
    else:
        print(f"* User {user_name} cannot leave {room_name}")
        return jsonify({"error": f"User {user_name} cannot leave {room_name}"}), 400

# Add a new message
@app.route("/add-message", methods=["POST"])
def add_message():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')
    msg = data.get('message')

    if not user_name or not room_name or not msg:
        return jsonify({"error": "user-name, room-name and message text are required to add message"}), 400

    user = search_user(user_name)
    room = search_room(room_name)
    if user == None or room == None:
        print(f"* User {user_name} cannot send message in room {room_name}")
        return jsonify({"error": f"User {user_name} cannot send message in room {room_name}"}), 400
    result = room.add_message(user, msg)
    if result == True:
        print(f"> User {user_name} sent message in room {room_name}")
        return jsonify({"success": f"User {user_name} sent message in room {room_name}"}), 200
    else:
        print(f"* User {user_name} cannot send message in room {room_name}")
        return jsonify({"error": f"User {user_name} cannot send message in room {room_name}"}), 400

# Get all the messages for a room
@app.route("/get-messages", methods=["POST"])
def get_messages():
    data = request.json
    room_name = data.get('room-name')
    if not room_name:
        return jsonify({"error": "room-name is required to get messages"}), 400
    print(f"> displaying messages in room {room_name}.")
    room = search_room(room_name)
    if room == None:
        return jsonify({"error": f"Room {room_name} does not exist"}), 400
    msg_objects = room.get_messages()
    msg_list = []
    for mo in msg_objects:
        msg_list.append(mo.get_user().user_name + ':\n' + mo.get_message())
    if len(msg_list) == 0:
        return jsonify({"error": f"No messages in room {room_name}"}), 400
    else:
        return jsonify({"success": msg_list}), 200


# Check if user can send message to a room
@app.route("/can-send", methods=["POST"])
def can_send():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to see if can send message"}), 400

    user = search_user(user_name)
    room = search_room(room_name)
    if user == None or room == None:
        print(f"* User {user_name} cannot send message in room {room_name}")
        return jsonify({"error": f"User {user_name} cannot send message in room {room_name}"}), 400
    return jsonify({"success": f"User {user_name} can send message in room {room_name}"}), 200
