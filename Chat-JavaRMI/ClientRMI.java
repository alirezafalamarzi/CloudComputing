import java.io.IOException;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.List;
import java.util.Scanner;


public class ClientRMI {
    private static User user;
    private static Scanner reader;
    private static String[] commandArgs;
    private static String command;
    private static ChatInterface stub;


    private static void addMessage(String client, String[] args) {
        try {
            for(int i = 1; i < args.length; i++) {
                if (!stub.canSendMessage(client, args[i])) {
                    print("> You can't send message to this room.");
                    return;
                }
            }
        } catch (RemoteException e) {
            throw new RuntimeException(e);
        }
        // Read line by line and send to the server.
        print("> Enter your message (Enter an empty line to send):");
        // Get the command and send it to the server
        StringBuilder stringBuilder = new StringBuilder();
        String line = "\t" + reader.nextLine() + "\n";
        while (!line.isBlank()) {
            stringBuilder.append(line);
            line = "\t" + reader.nextLine() + "\n";
        }
        try {
            for(int i = 1; i < args.length; i++) {
                if(stub.addMessage(client, args[i], stringBuilder.toString())) {
                    print("> Sent to " + args[i]);
                } else {
                    print("> Unable to send to " + args[i]);
                }
            }
        } catch (RemoteException e) {
            throw new RuntimeException(e);
        }

    }



    private static void print(String str) {
        System.out.println(str);
    }



    private static void getCommand() {
        print("> Enter command ('help' for list of commands):");
        // Get the command and send it to the server
        command = reader.nextLine();

        // Split the command to get its arguments
        commandArgs = command.split("\\s+");

        // If the command was "help" pring all these help text:
        if (command.equals("help"))
        {
            print("Available commands (<> is for mandatory args [] is for optional):");
            print("*Create new chatrooms:");
            print("  create <chatroom1> [chatroom2 chatroom3 ...]\n");
            print("*Join existing chatrooms:");
            print("  join <chatroom1> [chatroom2 chatroom3 ...]\n");
            print("*Leave previously joined chatrooms:");
            print("  leave <chatroom1> [chatroom2 chatroom3 ...]\n");
            print("*List all the names of existing chatrooms:");
            print("  list\n");
            print("*Display the messages in a single chatroom:");
            print("  display <chatroom1>\n");
            print("*Send a message to one or multiple chatrooms:");
            print("  send <chatroom1> [chatroom2 chatroom3 ...]\n");
            print("*Show this help text:");
            print("  help\n");
            return;
        }


        // handle wrong number of arguments for commands
        if (commandArgs != null) {
            if (
                    commandArgs[0].equals("send") ||
                            commandArgs[0].equals("join") ||
                            commandArgs[0].equals("leave") ||
                            commandArgs[0].equals("create")) {
                if (commandArgs.length < 2) {
                    print("> This command needs at least one argument");
                    return;
                }
            } else if (
                    commandArgs[0].equals("help") ||
                            commandArgs[0].equals("list")) {
                if (commandArgs.length > 1) {
                    print("> This command takes no argument.");
                    return;
                }
            } else if (commandArgs[0].equals("display")) {
                if (commandArgs.length != 2) {
                    print("> This command takes only 1 arguments.");
                    return;
                }
            }


            switch (commandArgs[0]) {
                case "create" -> {
                    for (int i = 1; i < commandArgs.length; i++) {
                        try {
                            if(stub.createRoom(commandArgs[i])) {
                                print("> Chatroom " + commandArgs[i] + " created.");
                            } else {
                                print("* Error creating chatroom " + commandArgs[i] + ".");
                            }

                        } catch (RemoteException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }

                case "join" -> {
                    for (int i = 1; i < commandArgs.length; i++) {
                        try {
                            ;
                            if(stub.joinRoom(user.getUsername(), commandArgs[i])) {
                                print("> You joined chatroom " + commandArgs[i] + ".");
                            } else {
                                print("* Error joining chatroom " + commandArgs[i] + ".");
                            }
                        } catch (RemoteException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }

                case "leave" -> {
                    for (int i = 1; i < commandArgs.length; i++) {
                        try {
                            if(stub.leaveRoom(user.getUsername(), commandArgs[i])) {
                                print("> You left chatroom " + commandArgs[i] + ".");
                            } else {
                                print("* Error leaving chatroom " + commandArgs[i] + ".");
                            }
                        } catch (RemoteException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }

                case "send" -> {
                    addMessage(user.getUsername(), commandArgs);
                }

                case "list" -> {
                    try {
                        String rooms = stub.getRooms(user.getUsername());
                        if(rooms == null || rooms.isEmpty()) {
                            print("> [There are no rooms]");
                            return;
                        }
                        print("> List of rooms:");
                        print(rooms);
                    } catch (RemoteException e) {
                        throw new RuntimeException(e);
                    }
                }

                case "display" -> {
                    try {
                        List<Message> messages = stub.getMessages(commandArgs[1]);
                        if(messages == null) {
                            print("> Room " + commandArgs[1] + " does not exist.");
                            return;
                        }
                        for (Message m: messages) {
                            print(m.getMsg());
                        }
                    } catch (RemoteException e) {
                        throw new RuntimeException(e);
                    }
                }

                case "quit" -> {
                    return;
                }

                default -> print("> Cannot run command " + command + ". Try again.");
            }
        }

    }

    private static boolean signup() {
        print("> Welcome to NetChat. Enter your username:");

        // Get the name of the user and send it to server
        var name = reader.nextLine();
        if (name != null) {
            try {
                user = stub.addClient(name);
            } catch (RemoteException e) {
                throw new RuntimeException(e);
            }
            if(user != null) {
                return true;
            }
        }
        return false;
    }


    public static void main(String[] args) {
        try {
            reader = new Scanner(System.in);


            /**
             * RMI Code
             */
            Registry registry = LocateRegistry.getRegistry("localhost");
            stub = (ChatInterface) registry.lookup("chatstub");

        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (NotBoundException e) {
            throw new RuntimeException(e);
        }

        // First try to signup. If failed try again.
        boolean success = false;
        while (!success) {
            success = signup();
        }

        // As long as the client is still connected
        while (true) {
            // Get a command from the use and send it to the server
            getCommand();
            // If the command was not "quit", then continue
            if (commandArgs != null && !commandArgs[0].equals("quit")) continue;
            // Otherwise close the connection and break
            break;
        }
    }
}

