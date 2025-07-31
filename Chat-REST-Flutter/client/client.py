import requests

SERVER_URL = "http://127.0.0.1:5000"


# Username of the current client
user_name = ''

# The current command
command = None

# The command arguments
args = []


def post(route, json_dict):
    return requests.post(f"{SERVER_URL}/{route}", json=json_dict)


# Gets a command from the user and sends it to the server using gRPC
def get_command():
    global args
    global user_name
    global command
    command = input("> Enter command ('help' for list of commands): ")
    args = command.split()
    if command == "help":
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
    if args != None and len(args) > 0:
        if (args[0] == "send" or
            args[0] == "join" or
            args[0] == "leave" or
            args[0] == "create"
        ):
            if len(args) < 2:
                print("> This command needs at least one argument")
                return
        elif args[0] == "help" or args[0] == "list":
            if len(args) > 1:
                print("> This command takes no argument.")
                return

        elif args[0] == "display":
            if len(args) != 2:
                print("> This command takes only 1 arguments.")
                return


        if args[0] == "create":
            for arg in args[1:]:
                result = post("create-room", {"room-name": arg})
                if result.status_code == 200:
                    print("> Chatroom " + arg + " created.")
                else:
                    print("* Error creating chatroom " + arg + ":")
                    print(result.json().get('error'))

        elif args[0] == "join":
            for arg in args[1:]:
                result = post("join-room", {"user-name": user_name, "room-name": arg})
                if result.status_code == 200:
                    print("> You joined chatroom " + arg + ".")
                else:
                    print("* Error joining chatroom " + arg + ".")
                    print(result.json().get('error'))

        elif args[0] == "leave":
            for arg in args[1:]:
                result = post("leave-room", {"user-name": user_name, "room-name": arg})
                if result.status_code == 200:
                    print("> You left chatroom " + arg + ".")
                else:
                    print("* Error leaving chatroom " + arg + ".")
                    print(result.json().get('error'))

        elif args[0] == "send":
            add_message()

        elif args[0] == "list":
            result = post("get-rooms", {"user-name": user_name})
            rooms = result.json().get('success')
            if rooms == '':
                print("> [There are no rooms]")
                return
            print("> List of rooms:")
            print(rooms)

        elif args[0] == "display":
            result = post('get-messages', {"room-name": args[1]})
            messages = result.json().get('success')
            if not messages:
                print("> Room " + args[1] + " does not exist.")
                return
            elif messages == []:
                print("> [There are no messages]")
                return
            else:
                for m in messages:
                    print(m)

        elif args[0] == "quit":
            return

        else:
            print("> Cannot run command " + command + ". Try again.")


# For adding a new message to the chatroom
def add_message():
    global args
    global command
    global user_name
    # Check if we can send message to all the rooms given in the command args
    for arg in args[1:]:
        result = post("can-send", {"user-name": user_name, "room-name": arg})
        if result.status_code != 200:
            print("> You can't send message to this room.")
            return

    # Get the text line by line
    text = ''
    line:str = input("> Enter your message (Enter an empty line to send): ")
    while(line != ''):
        text += '\t' + line + '\n'
        line = input('>>> ')

    # Send to the server
    for arg in args[1:]:
        result = post('add-message', {"user-name":user_name, "room-name":arg, "message":text})
        if result.status_code == 200:
            print("> Sent to " + arg)
        else:
            print("> Unable to send to " + arg)
            print(result.json().get('error'))



# Sign up a new client with a username
def sign_up():
    global user_name
    user_name = input("> Welcome to NetChat. Enter a unique username: ")
    if user_name != '':
        response = post("add-user", {"user-name": user_name})
        if response.status_code == 200:
            return True
    return False


def main():
    global command
    # Sign up as much as unique name is entered as username
    success = False
    while (not success):
        success = sign_up()

    # Infinitely get the command from the user and send it to server unless the user types quit.
    while True:
        get_command()
        if command != "quit": continue
        break


if __name__ == "__main__":
    main()
