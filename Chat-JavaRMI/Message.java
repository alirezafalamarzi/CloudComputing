import java.io.Serializable;

/**
 * The class that represents a message
 */
public class Message implements Serializable {
    /**
     * The actual message
     */
    private String msg;

    /**
     * The client that sent it.
     */
    private User user;

    public Message(User user, String msg) {
        this.user = user;
        this.msg = msg;
    }

    public String getMsg() {
        return user.getUsername() + ":\n" + msg;
    }

    public User getClient() {
        return user;
    }

}
