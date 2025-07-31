from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import redis as Redis

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

redis = Redis.StrictRedis(host='host.docker.internal', port=6379, decode_responses=True)


def get_room(room_name):
    room_data = redis.get(f"room:{room_name}")
    return json.loads(room_data) if room_data else None

def save_room(room_name, room_data):
    redis.set(f"room:{room_name}", json.dumps(room_data))
    redis.sadd("rooms", room_name)

def get_user(user_name):
    user_data = redis.get(f"user:{user_name}")
    return json.loads(user_data) if user_data else None

def save_user(user_name, user_data):
    redis.set(f"user:{user_name}", json.dumps(user_data))


@app.route("/create-room", methods=["POST"])
def create_room():
    data = request.json
    room_name = data.get('room-name')
    if not room_name:
        return jsonify({"error": "room-name is required to create a new room"}), 400
    if get_room(room_name):
        print(f"Error: {room_name} already exists.")
        return jsonify({"error": f"Room {room_name} already exists."}), 400
    room = {"room_name": room_name, "users": [], "messages": []}
    save_room(room_name, room)
    print("> Room " + room_name + " created.")
    return jsonify({"success": f"Room {room_name} created"}), 200


# Get all the rooms
@app.route("/get-rooms", methods=["GET"])
def get_rooms():
    room_names = redis.smembers("rooms")
    return jsonify({"rooms": list(room_names)}), 200

# Add a new user
@app.route("/add-user", methods=["POST"])
def add_user():
    data = request.json
    user_name = data.get('user-name')
    if not user_name:
        return jsonify({"error": "user-name is required to add user"}), 400
    if get_user(user_name):
        print(f"* Cannot add user {user_name}.")
        return jsonify({"error": "User already exists"}), 400
    user = {"user_name": user_name, "rooms": []}
    save_user(user_name, user)
    print(f"> User {user_name} was added.")
    return jsonify({"success": f"User {user_name} added"}), 200


# join a room
@app.route("/join-room", methods=["POST"])
def join_room():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to join room"}), 400

    user = get_user(user_name)
    room = get_room(room_name)
    if not user or not room:
        print(f"* User {user_name} cannot join {room_name}")
        return jsonify({"error": f"User {user_name} cannot join {room_name}"}), 400
    if user_name not in room["users"]:
        room["users"].append(user_name)
        save_room(room_name, room)
    if room_name not in user["rooms"]:
        user["rooms"].append(room_name)
        save_user(user_name, user)
    return jsonify({"success": f"User {user_name} joined room {room_name}"}), 200


# Leave a room
@app.route("/leave-room", methods=["POST"])
def leave_room():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to leave room"}), 400

    user = get_user(user_name)
    room = get_room(room_name)
    if not user:
        return jsonify({"error": f"User {user_name} does not exist"}), 400

    if not room:
        return jsonify({"error": f"Room {room_name} does not exist"}), 400

    if room_name not in user["rooms"]:
        return jsonify({"error": f"User {user_name} is not in room {room_name}"}), 400


     # Remove user from room
    if user_name in room["users"]:
        room["users"].remove(user_name)
        save_room(room_name, room)

    # Remove room from user
    if room_name in user["rooms"]:
        user["rooms"].remove(room_name)
        save_user(user_name, user)

    return jsonify({"success": f"User {user_name} left room {room_name}"}), 200

# Add a new message
@app.route("/add-message", methods=["POST"])
def add_message():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')
    msg = data.get('message')

    if not user_name or not room_name or not msg:
        return jsonify({"error": "user-name, room-name and message text are required to add message"}), 400

    room = get_room(room_name)
    if not room or user_name not in room["users"]:
        return jsonify({"error": "User not in room"}), 400

    message = {"user": user_name, "msg": msg}
    room["messages"].append(message)
    save_room(room_name, room)

    return jsonify({"success": "Message added"}), 200

# Get all the messages for a room
@app.route("/get-messages", methods=["POST"])
def get_messages():
    data = request.json
    room_name = data.get('room-name')
    if not room_name:
        return jsonify({"error": "room-name is required to get messages"}), 400
    print(f"> displaying messages in room {room_name}.")
    room = get_room(room_name)
    if not room:
        return jsonify({"error": "Room does not exist"}), 400

    return jsonify({"success": room["messages"]}), 200


# Check if user can send message to a room
@app.route("/can-send", methods=["POST"])
def can_send():
    data = request.json
    user_name = data.get('user-name')
    room_name = data.get('room-name')

    if not user_name or not room_name:
        return jsonify({"error": "user-name and room-name are required to see if can send message"}), 400

    room = get_room(room_name)
    if not room or user_name not in room["users"]:
        print(f"* User {user_name} cannot send message in room {room_name}")
        return jsonify({"error": f"User {user_name} cannot send message in room {room_name}"}), 400
    return jsonify({"success": f"User {user_name} can send message in room {room_name}"}), 200

