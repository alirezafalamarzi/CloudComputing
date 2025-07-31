import asyncio
import logging

import grpc
import chat_pb2
import chat_pb2_grpc

# Client class
class Client:
    def __init__(self):
        # Username of the current client
        self.user_name = ''

        # The stub function for gRPC
        self.stub:chat_pb2_grpc.ChatStub = None

        # The current command
        self.command = None

        # The command arguments
        self.args = []

    # Gets a command from the user and sends it to the server using gRPC
    def get_command(self):
        self.command:str = input("> Enter command ('help' for list of commands): ")
        self.args = self.command.split()
        if self.command == "help":
            print("Available commands (<> is for mandatory args [] is for optional): ")
            print("*Create new chatrooms:")
            print("  create <chatroom1> [chatroom2 chatroom3 ...]\n")
            print("*Join existing chatrooms:")
            print("  join <chatroom1> [chatroom2 chatroom3 ...]\n")
            print("*Leave previously joined chatrooms:")
            print("  leave <chatroom1> [chatroom2 chatroom3 ...]\n")
            print("*List all the names of existing chatrooms:")
            print("  list\n")
            print("*Display the messages in a single chatroom:")
            print("  display <chatroom1>\n")
            print("*Send a message to one or multiple chatrooms:")
            print("  send <chatroom1> [chatroom2 chatroom3 ...]\n")
            print("*Show this help text:")
            print("  help\n")
            print("*Quit:")
            print("  quit\n")
            return

        # Check for the correct number of args:
        if self.args != None and len(self.args) > 0:
            if (self.args[0] == "send" or
                self.args[0] == "join" or
                self.args[0] == "leave" or
                self.args[0] == "create"
            ):
                if len(self.args) < 2:
                    print("> This command needs at least one argument")
                    return
            elif self.args[0] == "help" or self.args[0] == "list":
                if len(self.args) > 1:
                    print("> This command takes no argument.")
                    return

            elif self.args[0] == "display":
                if len(self.args) != 2:
                    print("> This command takes only 1 arguments.")
                    return


            if self.args[0] == "create":
                for arg in self.args[1:]:
                    result = self.stub.CreateRoom(chat_pb2.Room(name=arg))
                    if result.flag == True:
                        print("> Chatroom " + arg+ " created.")
                    else:
                        print("* Error creating chatroom " + arg + ".")

            elif self.args[0] == "join":
                for arg in self.args[1:]:
                    result = self.stub.JoinRoom(chat_pb2.UserRoom(user=self.user_name, room=arg))
                    if result.flag == True:
                        print("> You joined chatroom " + arg + ".")
                    else:
                        print("* Error joining chatroom " + arg + ".")

            elif self.args[0] == "leave":
                for arg in self.args[1:]:
                    result = self.stub.LeaveRoom(chat_pb2.UserRoom(user=self.user_name, room=arg))
                    if result.flag == True:
                        print("> You left chatroom " + arg + ".")
                    else:
                        print("* Error leaving chatroom " + arg + ".")

            elif self.args[0] == "send":
                self.add_message()

            elif self.args[0] == "list":
                rooms = self.stub.GetRooms(chat_pb2.User(name=self.user_name))
                if rooms.text == '':
                    print("> [There are no rooms]")
                    return
                print("> List of rooms:")
                print(rooms.text)

            elif self.args[0] == "display":
                messages = self.stub.GetMessages(chat_pb2.Room(name=self.args[1]))
                if messages.text == None:
                    print("> Room " + self.args[1] + " does not exist.")
                    return
                elif messages.text == []:
                    print("> [There are no messages]")
                    return
                else:
                    for m in messages.text:
                        print(m)

            elif self.args[0] == "quit":
                return

            else:
                print("> Cannot run command " + self.command + ". Try again.")


    # For adding a new message to the chatroom
    def add_message(self):
        # Check if we can send message to all the rooms given in the command args
        for arg in self.args[1:]:
            result = self.stub.CanSend(chat_pb2.UserRoom(user=self.user_name, room=arg))
            if result.flag == False:
                print("> You can't send message to this room.")
                return

        # Get the text line by line
        text = ''
        line:str = input("> Enter your message (Enter an empty line to send): ")
        while(line != ''):
            text += '\t' + line + '\n'
            line = input('>>> ')

        # Send to the server
        for arg in self.args[1:]:
            result = self.stub.AddMessage(chat_pb2.UserRoomMessage(user=self.user_name, room=arg, msg=text))
            if result.flag == True:
                print("> Sent to " + arg)
            else:
                print("> Unable to send to " + arg)


    # Sign up a new client with a username
    def sign_up(self):
        self.user_name = input("> Welcome to NetChat. Enter a unique username: ")
        if self.user_name != '':
            result = self.stub.AddUser(chat_pb2.User(name=self.user_name))
        return result.flag


    # Run the gRPC client
    def run(self) -> None:
        # Connect to the server
        with grpc.insecure_channel("server:8080") as channel:
            self.stub = chat_pb2_grpc.ChatStub(channel)

            # Sign up as much as unique name is entered as username
            success = False
            while (not success):
                success = self.sign_up()

            # Infinitely get the command from the user and send it to server unless the user types quit.
            while True:
                self.get_command()
                if self.args != None and len(self.args) > 0 and self.args[0] != "quit": continue
                break


if __name__ == "__main__":
    logging.basicConfig()
    c = Client()
    c.run()
