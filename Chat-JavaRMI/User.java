import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * The class to hold info about a client
 */

public class User implements Serializable {
    private String username;
    private List<Room> rooms;

    public User(String username) {
        this.username = username;
        this.rooms = new ArrayList<>();
    }

    public boolean joinRoom(Room room) {
        if(!rooms.contains(room)) {
            rooms.add(room);
            return true;
        }
        return false;
    }

    public boolean leaveRoom(Room room) {
        return rooms.remove(room);
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String name) {
        this.username = name;
    }

    public boolean canSend(Room room) {
        return rooms.contains(room);
    }
}
