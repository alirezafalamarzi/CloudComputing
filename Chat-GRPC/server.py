import asyncio
import logging

import grpc
import chat_pb2
import chat_pb2_grpc


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


# Class for handling the chat using gRPC
class Chat(chat_pb2_grpc.ChatServicer):

    def __init__(self):
        # All the rooms
        self.rooms = []
        # All the users
        self.users = []

    # Search if a room exists and return it
    def search_room(self, room_name):
        for r in self.rooms:
            if r.room_name == room_name:
                return r
        return None
    # search if a user exists and return it
    def search_user(self, user_name):
        for u in self.users:
            if u.user_name == user_name:
                return u
        return None

    # Create a new room
    async def CreateRoom(self, request: chat_pb2.Room, context: grpc.aio.ServicerContext,) -> chat_pb2.Success:
        if self.search_room(request.name) == None:
            self.rooms.append(Room(request.name))
            print("> Room " + request.name + " created.")
            return chat_pb2.Success(flag=True)
        print("* Error: Cannot create room " + request.name + ".")
        return chat_pb2.Success(flag=False)

    # Remove a room
    async def RemoveRoom(self, request: chat_pb2.Room, context: grpc.aio.ServicerContext,) -> chat_pb2.Success:
        to_remove = self.search_room(request.name)
        if to_remove != None:
            self.rooms.remove(to_remove)
            print("> Room " + request.name + " removed.")
            return chat_pb2.Success(flag=True)
        print("* Cannot reamove room " + request.name + ".")
        return chat_pb2.Success(flag=False)


    # Get all the rooms
    async def GetRooms(self, request: chat_pb2.User, context: grpc.aio.ServicerContext) -> chat_pb2.Reply:
        rooms_list = ''
        user = self.search_user(request.name)
        for room in self.rooms:
            rooms_list += '\t' + room.get_name()
            if(room.has_user(user)):
                rooms_list += ' [joined]'
            rooms_list += '\n'
        print("> Listing the rooms for client " + request.name)
        return chat_pb2.Reply(text=rooms_list)

    # Add a new user
    async def AddUser(self, request: chat_pb2.User, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        if self.search_user(request.name) == None:
            self.users.append(User(request.name))
            print("> User " + request.name + " was added.")
            return chat_pb2.Success(flag=True)
        print("* Cannot add user " + request.name + ".")
        return chat_pb2.Success(flag=False)

    # Remove a user
    async def RemoveUser(self, request: chat_pb2.User, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        to_remove = self.search_user(request.name)
        if to_remove != None:
            self.users.remove(to_remove)
            for r in self.rooms:
                r.remove_user(to_remove)
            print("> User " + request.name + " was removed.")
            return chat_pb2.Success(flag=True)
        print("* Cannot remove user " + request.name + ".")
        return chat_pb2.Success(flag=False)

    # Join a room
    async def JoinRoom(self, request: chat_pb2.UserRoom, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        user = self.search_user(request.user)
        room = self.search_room(request.room)
        if user == None or room == None:
            print("* User " + request.user + " cannot join room " + request.room + ".")
            return chat_pb2.Success(flag=False)
        result = user.join_room(room) and room.add_user(user)
        print("> User " + request.user + " joined room " + request.room + ".")
        return chat_pb2.Success(flag=result)

    # Leave a room
    async def LeaveRoom(self, request: chat_pb2.UserRoom, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        user = self.search_user(request.user)
        room = self.search_room(request.room)
        if user == None or room == None:
            print("* User " + request.user + " cannot leave room " + request.room + ".")
            return chat_pb2.Success(flag=False)
        print("> User " + request.user + " left room " + request.room + ".")
        return chat_pb2.Success(flag= (user.leave_room(room) and room.remove_user(user)))

    # Add a new message
    async def AddMessage(self, request: chat_pb2.UserRoomMessage, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        user = self.search_user(request.user)
        room = self.search_room(request.room)
        if user == None or room == None:
            print("* User " + request.user + " cannot send message in room " + request.room + ".")
            return chat_pb2.Success(flag=False)
        print("> User " + request.user + " sent message in room " + request.room + ".")
        return chat_pb2.Success(flag= (room.add_message(user, request.msg)))

    # Get all the messages for a room
    async def GetMessages(self, request: chat_pb2.Room, context: grpc.aio.ServicerContext) -> chat_pb2.Messages:
        print("> displaying messages in room " + request.name + ".")
        room = self.search_room(request.name)
        if room == None:
            return chat_pb2.Messages(text=None)
        msg_objects = room.get_messages()
        msg_list = []
        for mo in msg_objects:
            msg_list.append(mo.get_user().user_name + ':\n' + mo.get_message())

        return chat_pb2.Messages(text=msg_list)

    # Check if user can send message to a room
    async def CanSend(self, request: chat_pb2.UserRoom, context: grpc.aio.ServicerContext) -> chat_pb2.Success:
        user = self.search_user(request.user)
        room = self.search_room(request.room)
        if user == None or room == None:
            return chat_pb2.Success(flag=False)
        return chat_pb2.Success(flag=user.can_send(room))

# Start the gRPC server
async def serve() -> None:
    server = grpc.aio.server()
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    listen_addr = "[::]:8080"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
