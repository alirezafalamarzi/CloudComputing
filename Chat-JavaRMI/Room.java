import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * The class that represents a chatroom
 */
public class Room implements Serializable {
    /**
     * The name of the chatroom
     */
    private String name;

    /**
     * The list of the clients in this chatroom
     */
    private List<User> users;


    /**
     * The list of all the messages in this chatroom
     */
    private List<Message> messages;

    public Room(String name) {
        this.name = name;
        users = new ArrayList<>();
        messages = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean addClient(User user) {
        if(!users.contains(user)) {
            users.add(user);
            return true;
        }
        return false;
    }

    public boolean removeClient(User user) {
        return users.remove(user);
    }

    public boolean hasUser(String userName) {
        for(User u: users) {
            if(u.getUsername().equals(userName)) {
                return true;
            }
        }
        return false;
    }

    public boolean addMessage(User user, String msg) {
        if(users.contains(user)) {
            messages.add(new Message(user, msg));
            return true;
        }
        return false;
    }

    public List<Message> getMessages() {
        return messages;
    }
}
