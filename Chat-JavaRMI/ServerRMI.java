import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

/**
 * The main class that contains the main method
 */
public class ServerRMI {
    public static void main(String[] args) throws Exception {
        Chat chat = new Chat();
        ChatInterface stub = (ChatInterface) UnicastRemoteObject.exportObject(chat, 0);

        Registry registry = LocateRegistry.getRegistry();
        registry.bind("chatstub", stub);
        System.out.println("RMI Server started...");
    }
}









