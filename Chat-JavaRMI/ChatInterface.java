import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface ChatInterface extends Remote {
    /**
     * Creates a new chatroom and adds it to the list
     * @param name the name of the chatroom
     * @return false if the chatroom exists already and true otherwise
     */
    boolean createRoom(String name) throws RemoteException;

    /**
     * Removes a chatroom
     * @param name the name of the chatroom
     * @return true if chatroom exists and it got removed. false otherwise.
     */
    boolean removeRoom(String name) throws RemoteException;

    /**
     * Search for a room in the list and return it if it exists
     * @param name the name of the chatroom to look for
     * @return the room we are looking for if it exists otherwise null
     */
    Room searchRoom(String name) throws RemoteException;

    /**
     * Get a list of all the rooms
     * @return a list of all the rooms
     */
    String getRooms(String userName) throws RemoteException;

    /**
     * add a new client
     * @param username the name of the new client
     * @return the newly created client if it exists or if it already exist null
     */
    User addClient(String username) throws RemoteException;

    /**
     * remove a client
     * @param username the name of the client
     * @return true if the client existed and got removed, false otherwise
     */
    boolean removeClient(String username) throws RemoteException;

    /**
     * Search for a client and return it if found
     * @param username the name of the client to look for
     * @return the client if found or null otherwise.
     */
    User searchClient(String username) throws RemoteException;

    /**
     * Join a client to a room
     * @param clientName the client that wants to be joined
     * @param roomName the room that the client is joining
     * @return true if join was successful or false otherwise
     */
    boolean joinRoom(String clientName, String roomName) throws RemoteException;

    /**
     * Make a client leave a chatroom
     * @param clientName the client that wants to leave
     * @param roomName the room which the client wants to leave
     * @return true if leaving was successful or false otherwise
     */
    boolean leaveRoom(String clientName, String roomName)throws RemoteException;

    /**
     * Get a list of all the messages of a chatroom
     * @param roomName the chatroom
     * @return the list of all the messages
     */
    List<Message> getMessages(String roomName) throws RemoteException;

    /**
     * See if a client can send a message to a room
     * @param clientName the client that wants to send a message
     * @param roomName the room the client wants to send a message into
     * @return true if successful false otherwise.
     */
    boolean canSendMessage(String clientName, String roomName) throws RemoteException;

    /**
     * Add a new message to the chatroom
     * @param clientName the client that wrote the message
     * @param roomName the chatroom
     * @param msg the message
     * @return true if successful or false otherwise
     */
    boolean addMessage(String clientName, String roomName, String msg) throws RemoteException;
}
