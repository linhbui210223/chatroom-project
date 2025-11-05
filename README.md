# Secure Multi-User Chat Application

A secure, feature-rich chat application built with Python that supports real-time communication, private messaging, file sharing, emoji support, and end-to-end encryption.

## Features

### Core Functionality
- **Real-time Communication**: Instant message delivery using socket programming
- **Multi-user Support**: Multiple clients can connect simultaneously
- **Private Messaging**: Send direct messages to specific users
- **Broadcast Messaging**: Send messages to all connected users
- **File Sharing**: Share files with all users or specific individuals (up to 10MB)
- **Emoji Support**: Full emoji support using shortcodes (e.g., `:smile:`, `:heart:`)

### Security Features
- **End-to-End Encryption**: All messages are encrypted using Fernet symmetric encryption
- **Secure Socket Communication**: Encrypted data transmission over TCP sockets
- **Username Validation**: Prevents duplicate usernames
- **Input Sanitization**: Proper handling of user inputs

### Technical Features
- **Client-Server Architecture**: Centralized server managing multiple clients
- **Concurrent Connection Handling**: Thread-based handling for multiple simultaneous users
- **Thread-Safe Operations**: Proper locking mechanisms for shared resources
- **Graphical User Interface**: Intuitive GUI built with Tkinter
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture

### Server (`server.py`)
- Manages client connections using socket programming
- Handles user authentication and session management
- Routes messages (broadcast and private)
- Manages file transfers
- Uses threading for concurrent client handling
- Implements thread-safe operations with locks

### Client (`client.py`)
- Connects to server using TCP sockets
- Provides GUI for user interaction
- Handles message encryption/decryption
- Supports emoji rendering
- Manages file uploads and downloads
- Runs message receiving in a separate thread

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/linhbui210223/chatroom-project.git
cd chatroom-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

1. Run the server:
```bash
python server.py
```

2. The server will start on `127.0.0.1:5555` by default
3. Note the encryption key displayed in the console (for debugging purposes)

### Starting the Client

1. Run the client:
```bash
python client.py
```

2. Enter your username and server details in the login window
3. Click "Connect" to join the chat

### Using the Chat Application

#### Sending Messages
- **Broadcast Message**: Type your message and press Enter or click "Send" (with "All Users" selected)
- **Private Message**: Select a user from the list, type your message, and send

#### Using Emojis
- Click the "😀" button to open the emoji picker
- Or type emoji codes directly (e.g., `:smile:`, `:heart:`, `:thumbsup:`)

#### Sharing Files
1. Click the "📎 File" button
2. Select a file (max 10MB)
3. File will be sent to the selected recipient (all users or specific user)
4. Recipients will be prompted to save the file

#### User List
- The right panel shows all online users
- Select "All Users" for broadcast messages
- Select a specific user for private messages

## Security Implementation

### Encryption
- Uses **Fernet** symmetric encryption from the `cryptography` library
- Server generates a unique encryption key per session
- All messages and files are encrypted before transmission
- Automatic encryption/decryption on both ends

### Data Protection
- Passwords/keys are not stored permanently
- Secure socket communication (can be upgraded to SSL/TLS)
- Input validation and sanitization

## Project Structure

```
chatroom-project/
├── server.py           # Server-side application
├── client.py           # Client-side application with GUI
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Dependencies

- **cryptography**: End-to-end encryption (Fernet)
- **emoji**: Emoji support and rendering

## Network Protocol

### Message Format
All messages are JSON-encoded and encrypted:

```json
{
  "type": "broadcast|private|file|user_list",
  "content": "message content",
  "recipient": "username (for private messages)",
  "filename": "file.txt (for files)",
  "data": "base64-encoded file data"
}
```

### Connection Flow
1. Client connects to server
2. Server sends encryption key
3. Client sends encrypted username
4. Server validates and confirms
5. Bidirectional encrypted communication begins

## Concurrency and Thread Safety

### Server
- Main thread accepts new connections
- Each client gets a dedicated handler thread
- Shared resources (client lists, usernames) protected with locks
- Thread-safe message broadcasting

### Client
- Main thread runs the GUI
- Separate thread handles incoming messages
- Thread-safe GUI updates using `root.after()`

## Limitations and Future Enhancements

### Current Limitations
- File size limited to 10MB
- No persistent message history
- Server runs on single machine
- No user authentication (only username check)

### Potential Enhancements
- Database integration for message history
- User authentication with passwords
- Group chat rooms
- Voice/video chat support
- End-to-end encryption with public/private keys
- SSL/TLS for transport security
- Message read receipts
- Typing indicators
- Profile pictures and user status

## Testing

### Manual Testing

1. **Start the server**:
```bash
python server.py
```

2. **Start multiple clients** (in separate terminals/windows):
```bash
python client.py
```

3. **Test broadcast messaging**:
   - Send messages with "All Users" selected
   - Verify all clients receive the message

4. **Test private messaging**:
   - Select a specific user from the list
   - Send a private message
   - Verify only that user receives it

5. **Test file sharing**:
   - Send a small file to all users or specific user
   - Verify file can be saved and opened

6. **Test emoji support**:
   - Send messages with emoji codes like `:smile:`
   - Use the emoji picker button
   - Verify emojis display correctly

7. **Test concurrent connections**:
   - Connect 5+ clients simultaneously
   - Send messages from multiple clients
   - Verify no race conditions or lost messages

## Troubleshooting

### Connection Issues
- Ensure server is running before starting clients
- Check firewall settings allow connections on port 5555
- Verify correct host and port in client login

### Username Taken
- Each username must be unique
- Try a different username if yours is taken

### File Transfer Issues
- Ensure file size is under 10MB
- Check file permissions and disk space
- Verify file path is accessible

## License

This project is open source and available for educational purposes.

## Author

Linh Bui

## Acknowledgments

- Built as a demonstration of secure network programming
- Implements best practices for socket programming and encryption
- Educational project showcasing client-server architecture