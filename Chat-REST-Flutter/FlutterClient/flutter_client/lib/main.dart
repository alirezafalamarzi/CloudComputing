import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  @override
  LoginScreenState createState() => LoginScreenState();
}

class LoginScreenState extends State<LoginScreen> {
  final TextEditingController usernameController = TextEditingController();
  bool isLoading = false;

  Future<void> login() async {
    String username = usernameController.text.trim();
    if (username.isEmpty) {
      showError("Username cannot be empty.");
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final url = Uri.parse('http://127.0.0.1:5000/add-user');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user-name': username}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        if (responseData['success'] != null) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SecondScreen(username: username),
            ),
          );
        } else {
          showError(responseData['error'] ?? "Unknown error occurred.");
        }
      } else {
        showError("Failed to connect to server. Please try again.");
      }
    } catch (e) {
      showError("An error occurred: $e");
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Login"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: usernameController,
              decoration: InputDecoration(
                labelText: "Enter your username",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20),
            isLoading
                ? CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: login,
                    child: Text("Login"),
                  ),
          ],
        ),
      ),
    );
  }
}

class SecondScreen extends StatefulWidget {
  final String username;

  SecondScreen({required this.username});

  @override
  SecondScreenState createState() => SecondScreenState();
}

class SecondScreenState extends State<SecondScreen> {
  final TextEditingController chatroomController = TextEditingController();
  final TextEditingController messageController = TextEditingController();
  String? selectedChatroom;
  List<String> chatrooms = [];
  List<String> joinedRooms = [];
  List<String> messages = [];
  Timer? refreshTimer;

  @override
  void initState() {
    super.initState();
    fetchChatrooms();
    startAutoRefresh();
  }

  @override
  void dispose() {
    refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> fetchChatrooms() async {
    try {
      final url = Uri.parse('http://127.0.0.1:5000/get-rooms');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user-name': widget.username}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        if (responseData['success'] != null) {
          List<String> fetchedRooms = responseData['success']
              .toString()
              .split('\n') // Split by lines
              .map((room) => room.trim()) // Trim whitespace
              .where((room) => room.isNotEmpty) // Filter out empty lines
              .toList();

          List<String> cleanRooms = [];
          List<String> joinedRoomsTemp = [];

          for (String room in fetchedRooms) {
            if (room.endsWith("[joined]")) {
              String cleanRoom = room.replaceAll("[joined]", "").trim();
              cleanRooms.add(cleanRoom);
              joinedRoomsTemp.add(cleanRoom);
            } else {
              cleanRooms.add(room);
            }
          }

          setState(() {
            chatrooms = cleanRooms;
            joinedRooms = joinedRoomsTemp;
            if (selectedChatroom != null &&
                !chatrooms.contains(selectedChatroom)) {
              selectedChatroom = null; // Reset selection if invalid
            }
          });
        }
      } else {
        showError("Failed to fetch chatrooms.");
      }
    } catch (e) {
      showError("Error fetching chatrooms: $e");
    }
  }

  Future<void> createChatroom() async {
    String chatroomName = chatroomController.text.trim();
    if (chatroomName.isEmpty) {
      showError("Chatroom name cannot be empty.");
      return;
    }

    try {
      final url = Uri.parse('http://127.0.0.1:5000/create-room');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'room-name': chatroomName}),
      );

      if (response.statusCode == 200) {
        chatroomController.clear();
        await fetchChatrooms(); // Refresh the list of rooms.
        showSuccess("Chatroom created successfully.");
      } else {
        final responseData = jsonDecode(response.body);
        showError(responseData['error'] ?? "Failed to create chatroom.");
      }
    } catch (e) {
      showError("Error creating chatroom: $e");
    }
  }

  Future<void> joinRoom() async {
    if (selectedChatroom == null || joinedRooms.contains(selectedChatroom)) {
      return;
    }

    try {
      final url = Uri.parse('http://127.0.0.1:5000/join-room');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user-name': widget.username,
          'room-name': selectedChatroom,
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          joinedRooms.add(selectedChatroom!);
        });
      }
    } catch (e) {
      showError("Error joining room: $e");
    }
  }

  Future<void> leaveRoom() async {
    if (selectedChatroom == null || !joinedRooms.contains(selectedChatroom)) {
      return;
    }

    try {
      final url = Uri.parse('http://127.0.0.1:5000/leave-room');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user-name': widget.username,
          'room-name': selectedChatroom,
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          joinedRooms.remove(selectedChatroom);
        });
      }
    } catch (e) {
      showError("Error leaving room: $e");
    }
  }

  Future<void> fetchMessages() async {
    if (selectedChatroom == null) return;

    try {
      final url = Uri.parse('http://127.0.0.1:5000/get-messages');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'room-name': selectedChatroom}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        setState(() {
          messages = responseData['success'] != null
              ? List<String>.from(responseData['success'])
              : ["No messages"];
        });
      } else {
        setState(() {
          messages = ["No messages"];
        });
      }
    } catch (e) {
      showError("Error fetching messages: $e");
    }
  }

  Future<void> sendMessage() async {
    String message = messageController.text.trim();
    if (selectedChatroom == null || message.isEmpty) {
      showError("Select a chatroom and enter a message.");
      return;
    }

    try {
      final url = Uri.parse('http://127.0.0.1:5000/add-message');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user-name': widget.username,
          'room-name': selectedChatroom,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        if (responseData['success'] != null) {
          messageController.clear();
          fetchMessages(); // Refresh messages after sending.
          showSuccess("Message sent.");
        } else {
          showError(responseData['error'] ?? "Failed to send message.");
        }
      } else {
        showError("Failed to send message. Please try again.");
      }
    } catch (e) {
      showError("Error sending message: $e");
    }
  }

  void startAutoRefresh() {
    refreshTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (selectedChatroom != null) fetchMessages();
    });
  }

  void showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Chatrooms"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: chatroomController,
                    decoration: InputDecoration(
                      labelText: "Enter chatroom name",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: createChatroom,
                  child: Text("Create Chatroom"),
                ),
              ],
            ),
            SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: DropdownButton<String>(
                    value: selectedChatroom,
                    isExpanded: true,
                    hint: Text("Select a chatroom"),
                    items: chatrooms.map((room) {
                      return DropdownMenuItem(
                        value: room,
                        child: Text(room),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedChatroom = value;
                      });
                    },
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: joinRoom,
                  child: Text("Join"),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: leaveRoom,
                  child: Text("Leave"),
                ),
              ],
            ),
            SizedBox(height: 10),
            if (selectedChatroom != null) ...[
              Text(
                joinedRooms.contains(selectedChatroom!)
                    ? "Status: Joined"
                    : "Status: Not Joined",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
            SizedBox(height: 20),
            Expanded(
              child: Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(5),
                ),
                child: messages.isEmpty
                    ? Center(child: Text("No messages"))
                    : ListView.builder(
                        itemCount: messages.length,
                        itemBuilder: (context, index) {
                          return Text(messages[index]);
                        },
                      ),
              ),
            ),
            SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: messageController,
                    decoration: InputDecoration(
                      labelText: "Enter message",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: sendMessage,
                  child: Text("Send"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
