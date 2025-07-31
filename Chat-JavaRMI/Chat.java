import java.util.ArrayList;
import java.util.List;

/**
 * Class that contains all the functionalities of the chat.
 */
public class Chat implements ChatInterface {
    /**
     * All the chatrooms
     */
    private final List<Room> rooms;

    /**
     * All the clients
     */
    private final List<User> users;

    public Chat() {
        this.rooms = new ArrayList<>();
        this.users = new ArrayList<>();
    }

    /**
     * Creates a new chatroom and adds it to the list
     * @param name the name of the chatroom
     * @return false if the chatroom exists already and true otherwise
     */
    public synchronized boolean createRoom(String name) {
        if(searchRoom(name) == null) {
            rooms.add(new Room(name));
            return true;
        }
        return false;
    }

    /**
     * Removes a chatroom
     * @param name the name of the chatroom
     * @return true if chatroom exists and it got removed. false otherwise.
     */
    public synchronized boolean removeRoom(String name) {
        Room toRemove = searchRoom(name);
        if(toRemove != null) {
            rooms.remove(toRemove);
            return true;
        }
        return false;
    }

    /**
     * Search for a room in the list and return it if it exists
     * @param name the name of the chatroom to look for
     * @return the room we are looking for if it exists otherwise null
     */
    public synchronized Room searchRoom(String name) {
        for(Room r: rooms) {
            if(r.getName().equals(name)) {
                return r;
            }
        }
        return null;
    }

    /**
     * Get a list of all the rooms
     * @return a list of all the rooms
     */
    public synchronized String getRooms(String userName) {
        StringBuilder builder = new StringBuilder();
        for(Room r: rooms) {
            builder.append("\t" + r.getName());
            if(r.hasUser(userName)) {
                builder.append(" [joined]");
            }
            builder.append("\n");
        }
        return builder.toString();
    }


    /**
     * add a new client
     * @param username the name of the new client
     * @return the newly created client if it exists or if it already exist null
     */
    public synchronized User addClient(String username) {
        if(searchClient(username) == null) {
            User newUser = new User(username);
            users.add(newUser);
            return newUser;
        }
        return null;
    }

    /**
     * remove a client
     * @param username the name of the client
     * @return true if the client existed and got removed, false otherwise
     */
    public synchronized boolean removeClient(String username) {
        User toRemove = searchClient(username);
        if(toRemove != null) {
            users.remove(toRemove);
            for(Room r: rooms) {
                r.removeClient(toRemove);
            }
            return true;
        }
        return false;
    }

    /**
     * Search for a client and return it if found
     * @param username the name of the client to look for
     * @return the client if found or null otherwise.
     */
    public synchronized User searchClient(String username) {
        for(User c: users) {
            if(c.getUsername().equals(username)) {
                return c;
            }
        }
        return null;
    }

    /**
     * Join a client to a room
     * @param userName the client that wants to be joined
     * @param roomName the room that the client is joining
     * @return true if join was successful or false otherwise
     */
    public synchronized boolean joinRoom(String userName, String roomName) {
        User user = searchClient(userName);
        Room room = searchRoom(roomName);
        if(user == null || room == null) {
            return false;
        }
        return user.joinRoom(room) && room.addClient(user);
    }

    /**
     * Make a client leave a chatroom
     * @param userName the client that wants to leave
     * @param roomName the room which the client wants to leave
     * @return true if leaving was successful or false otherwise
     */
    public synchronized boolean leaveRoom(String userName, String roomName) {
        User user = searchClient(userName);
        Room room = searchRoom(roomName);
        if(user == null || room == null) {
            return false;
        }
        return user.leaveRoom(room) && room.removeClient(user);
    }

    /**
     * Add a new message to the chatroom
     * @param userName the client that wrote the message
     * @param roomName the chatroom
     * @param msg the message
     * @return true if successful or false otherwise
     */
    public synchronized boolean addMessage(String userName, String roomName, String msg) {
        User user = searchClient(userName);
        Room room = searchRoom(roomName);
        if(user == null || room == null) {
            return false;
        }
        return room.addMessage(user, msg);
    }

    /**
     * Get a list of all the messages of a chatroom
     * @param roomName the chatroom
     * @return the list of all the messages
     */
    public synchronized List<Message> getMessages(String roomName) {
        Room room = searchRoom(roomName);
        if(room == null) {
            return null;
        }
        return room.getMessages();
    }

    /**
     * See if a client can send a message to a room
     * @param userName the client that wants to send a message
     * @param roomName the room the client wants to send a message into
     * @return true if successful false otherwise.
     */
    public synchronized boolean canSendMessage(String userName, String roomName) {
        User user = searchClient(userName);
        Room room = searchRoom(roomName);
        if(user == null || room == null) {
            return false;
        }
        return user.canSend(room);
    }
}

