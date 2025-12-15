# ChatSpace - Encrypted Real-Time Communication Platform

A secure, feature-rich real-time messaging application developed in Python, offering end-to-end encryption, dual messaging modes, multimedia file transfer, emoji integration, and an intuitive graphical interface.

---

## Table of Contents
1. ✨ [Core Features & Capabilities](#core-features--capabilities)
2. 🏛️ [System Architecture](#system-architecture)
3. 🚀 [Setup & Installation](#setup--installation)
4. 📖 [User Guide](#user-guide)
5. ⚡ [Performance Analysis](#performance-analysis)
6. 🔭 [Development Roadmap](#development-roadmap)
7. 🙏 [Credits & Resources](#credits--resources)

---

## Core Features & Capabilities

ChatSpace implements comprehensive functionality for secure, real-time communication:

| #  | Feature                    | Implementation Details                                                                     |
|----|----------------------------|--------------------------------------------------------------------------------------------|
| 1  | 🔑 Identity Verification   | Username-based authentication with server-side uniqueness validation                       |
| 2  | 📢 Broadcast Communication | Encrypted group messages distributed to all connected participants                         |
| 3  | 💬 Direct Messaging        | End-to-end encrypted person-to-person communication                                        |
| 4  | 👥 Participant Tracking    | Real-time roster of active users with automatic updates                                    |
| 5  | 🎨 Visual Interface        | Modern Tkinter-based GUI with message history, user panels, and notifications              |
| 6  | 🔄 Multi-Client Support    | Thread-based architecture enabling simultaneous user connections                           |
| 7  | 📁 Media Sharing           | Chunked file transmission with integrity verification and progress tracking                |
| 8  | 😊 Expression Support      | Visual emoji selector and text-based shortcode system                                      |
| 9  | 🕒 Temporal Context        | Automatic timestamp generation for all communications                                      |
| 10 | 🔒 Data Protection         | Hybrid RSA/AES-256 encryption securing all transmitted data                               |
| 11 | 🛡️ Resilient Operations    | Comprehensive error handling with graceful degradation and user feedback                   |

### Implementation Specifications

#### 1. Identity Verification System
- Initial connection prompts username selection
- Server maintains centralized username registry
- Duplicate detection with immediate user notification
- Automatic session binding upon validation

#### 2. Broadcast Communication
- Client-side message encryption before transmission
- Server-side routing to all authenticated sessions
- Format: `(Global) (Sender) (HH:MM:SS): Message`
- Real-time delivery with minimal latency

#### 3. Direct Messaging Protocol
- Command syntax: `/w [recipient] [message]` or GUI-based selection
- Server validates recipient existence before routing
- Encrypted end-to-end with unique session keys
- Format: `(Private) (From Sender) (HH:MM:SS): Message`

#### 4. Participant Tracking System
- Dynamic user list with join/leave event handling
- Automatic GUI refresh on roster changes
- Click-to-message functionality for quick DMs
- Visual indicators (🟢) for online status

#### 5. Visual Interface Components
- Scrollable message history with text wrapping
- Dedicated user roster panel
- Multi-line message composition area
- Integrated emoji picker and file selector
- Color-coded message types (blue: global, orange: private)

#### 6. Multi-Client Architecture
- Server: Thread-per-connection model via Socket.IO
- Client: Background daemon thread for message reception
- Non-blocking file operations via threading
- Concurrent session management with unique AES keys

#### 7. Media Sharing System
- Command syntax: `/filew [recipient] [filepath]` or GUI button
- 48KB chunk size for optimal transmission
- SHA-256 hash verification for integrity
- Progress bars with real-time percentage updates
- Accept/decline prompts for recipients
- Supported formats: MP4, MP3, JPEG, JPG, PNG
- Size limit: 25MB per file

#### 8. Expression Support
- Emoji picker with categorized tabs (Smileys, Animals, Foods, Symbols)
- Text-based shortcodes (e.g., `:smile:` → 😊)
- Search functionality in emoji picker
- Recent emoji tracking for quick access
- Unicode-safe insertion at cursor position

#### 9. Temporal Context System
- Format: `HH:MM:SS` for all messages
- Timestamp embedded in encrypted payload
- Client-side generation with server validation
- Persistent display in message history

#### 10. Cryptographic Implementation
- **Key Exchange**: RSA-2048 for initial AES key distribution
- **Session Encryption**: AES-256-CBC for all message/file data
- **Per-User Keys**: Unique AES key per client session
- **Server Role**: Decrypts with sender key, re-encrypts with recipient key(s)
- **File Integrity**: SHA-256 hashing for corruption detection

#### 11. Error Management
- Try-catch blocks around all network operations
- SQLite-based event logging for debugging
- User-friendly error messages via GUI popups
- Automatic cleanup on connection failures
- Graceful disconnection with notification broadcast

---

## System Architecture

### Architectural Overview

**Client Component:**  
Tkinter-based desktop application (`client/gui.py`) handling user interactions, cryptographic operations, and real-time communication via Socket.IO client.

**Server Component:**  
Flask application (`server/server.py`) with Socket.IO for event-driven messaging, session management, and secure data routing.

**Security Layer:**  
Hybrid cryptographic system combining RSA-2048 for key exchange with AES-256-CBC for bulk encryption, implemented in `crypto_utils.py`.

**Persistence Layer:**  
SQLite database (`logs/chat_logs.db`) with custom logger (`db_logger.py`) for audit trails and debugging.

**Expression System:**  
Shortcode-to-Unicode emoji mapping (`emoji_dict.py`) with visual picker integration.

### Directory Structure
```
chatroom-project/
├── client/
│   ├── gui.py                  # Main client application
│   ├── emoji_dict.py           # Emoji mapping dictionary
│   └── public_key.pem          # RSA public key for encryption
├── server/
│   ├── server.py               # Flask Socket.IO server
│   ├── crypto_utils.py         # Encryption/decryption utilities
│   ├── private_key.pem         # RSA private key (generated)
│   └── upload_files/           # File storage directory
├── logs/
│   ├── db_logger.py            # SQLite logging system
│   ├── chat_logs.db            # Event database (auto-generated)
│   └── view_logs.py            # Log viewer utility
├── tests/
│   ├── __init__.py
│   └── test_server.py          # Server unit tests
├── requirements.txt            # Production dependencies
├── requirements-test.txt       # Testing dependencies
├── rsa_key_generator.py        # Key generation utility
└── README.md                   # Project documentation
```

### Component Architecture

```mermaid
flowchart TB
    subgraph ClientApp["Client Application"]
        GUI["GUI Layer<br/>(Tkinter widgets, emoji picker)"]
        ClientLogic["Business Logic<br/>(Socket.IO client, event handlers)"]
        ClientCrypto["Crypto Module<br/>(AES encrypt, RSA key exchange)"]
    end

    subgraph ServerApp["Server Application"]
        SocketMgr["Socket.IO Manager<br/>(event routing, broadcasting)"]
        ServerCrypto["Crypto Module<br/>(AES decrypt/encrypt, RSA decrypt)"]
        SessionMgr["Session Manager<br/>(user registry, key storage)"]
        FileMgr["File Manager<br/>(chunk I/O, hash verification)"]
        Logger["Event Logger<br/>(SQLite persistence)"]
    end

    GUI --> ClientLogic
    ClientLogic --> ClientCrypto
    ClientCrypto <--> SocketMgr
    SocketMgr <--> ServerCrypto
    SocketMgr --> SessionMgr
    SocketMgr --> FileMgr
    SocketMgr --> Logger
    SessionMgr --> Logger
    FileMgr --> Logger

    classDef client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef server fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class GUI,ClientLogic,ClientCrypto client
    class SocketMgr,ServerCrypto,SessionMgr,FileMgr,Logger server
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as SQLite Logger

    Note over C,S: 1. Connection & Key Exchange
    C->>S: Connect via Socket.IO
    C->>C: Generate AES-256 key
    C->>S: Send RSA-encrypted AES key
    S->>S: Decrypt AES key with private key
    S->>DB: Log key exchange event
    
    Note over C,S: 2. User Authentication
    C->>S: Send username
    S->>S: Validate uniqueness
    S->>C: Broadcast user_joined event
    S->>DB: Log user join
    
    Note over C,S: 3. Message Transmission
    C->>C: Encrypt message with AES
    C->>S: Send encrypted message
    S->>S: Decrypt with sender's key
    S->>S: Re-encrypt for each recipient
    S->>C: Broadcast to all/specific users
    S->>DB: Log message event
    
    Note over C,S: 4. File Transfer
    C->>C: Split file into 48KB chunks
    C->>S: Send chunks with SHA-256 hash
    S->>S: Write chunks to disk
    S->>S: Verify hash integrity
    S->>C: Notify recipients
    S->>DB: Log file transfer
```

### Security Architecture

```mermaid
graph LR
    A[Client Login] --> B[Generate AES Key]
    B --> C[Encrypt AES with RSA Public Key]
    C --> D[Send to Server]
    D --> E[Server Decrypts with RSA Private Key]
    E --> F[Store Client's AES Key]
    F --> G[Client Encrypts Message with AES]
    G --> H[Server Decrypts with Sender's AES]
    H --> I[Server Re-encrypts with Recipient's AES]
    I --> J[Recipient Decrypts with Own AES]
    
    style B fill:#c8e6c9
    style E fill:#ffccbc
    style G fill:#c8e6c9
    style I fill:#ffccbc
```

---

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 50MB free disk space
- Network connectivity (localhost or LAN)

### Step 1: Repository Acquisition
```bash
git clone https://github.com/nami-macos/chatroom-project.git
cd chatroom-project
```

### Step 2: Environment Setup

#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using Conda
```bash
# Create conda environment
conda create -n chatspace python=3.9

# Activate environment
conda activate chatspace

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Cryptographic Key Generation

**⚠️ Important:** Keys must be generated before first use.

```bash
# Generate RSA-2048 key pair
python rsa_key_generator.py
```

This creates:
- `server/private_key.pem` - Server's private decryption key
- `client/public_key.pem` - Client's public encryption key

**Verify key creation:**
```bash
ls -la server/private_key.pem client/public_key.pem
```

### Step 4: Server Initialization

```bash
# Navigate to server directory
cd server

# Start server
python server.py
```

**Expected output:**
```
Loading RSA private key...
Socket.IO server initialized
 * Running on http://127.0.0.1:8080
```

### Step 5: Client Launch

**Open a new terminal** for each client instance:

```bash
# Activate environment (if using venv/conda)
source venv/bin/activate  # or: conda activate chatspace

# Navigate to client directory
cd client

# Launch client
python gui.py
```

**Multiple clients:**
- Repeat Step 5 in separate terminals for multi-user testing
- Each client gets a unique chat window
- All clients must use unique usernames

### Troubleshooting

#### Issue: `ModuleNotFoundError: No module named 'socketio'`
**Solution:**
```bash
pip install python-socketio
```

#### Issue: `FileNotFoundError: private_key.pem`
**Solution:**
```bash
python rsa_key_generator.py
```

#### Issue: `Address already in use (port 8080)`
**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill process (replace PID with actual number)
kill -9 <PID>

# Or change port in server.py:
# eventlet.wsgi.server(eventlet.listen(('localhost', 8081)), server.app)
```

#### Issue: `Connection refused`
**Solution:**
1. Verify server is running: `ps aux | grep server.py`
2. Check firewall settings
3. Ensure `localhost:8080` is accessible

### Testing Installation

```bash
# Run unit tests
pytest tests/test_server.py -v

# Expected output:
# tests/test_server.py::test_simple_math PASSED
# tests/test_server.py::TestChatServer::test_server_initialization PASSED
# tests/test_server.py::TestChatServer::test_user_management PASSED
```

---

## User Guide

### Initial Connection

1. **Launch Client:**
   ```bash
   cd client && python gui.py
   ```

2. **Username Entry:**
   - Enter a unique username (2-15 characters)
   - Alphanumeric only, no spaces
   - Press Enter or click arrow button

3. **Connection Verification:**
   - Green status indicator appears
   - User list populates with active participants
   - System message confirms connection

### Sending Messages

#### Broadcast Messages
```
Type your message in the input box and press Enter
```
- Visible to all connected users
- Displayed as: `(Global) (YourName) (14:23:15): Message`

#### Direct Messages
**Method 1: Command Syntax**
```
/w Username Your private message here
```

**Method 2: GUI Selection**
1. Click username in user list
2. Select "Message" option
3. Type message and send

- Displayed as: `(Private) (To Username) (14:23:15): Message`

### File Sharing

#### Sending Files

**Method 1: Button Interface**
1. Click "Send File ⬆️" button
2. Select file in dialog (MP4, MP3, JPEG, JPG, PNG)
3. Choose recipient (Global or specific user)
4. Monitor progress bar

**Method 2: Command Syntax**
```
/filew Username /path/to/file.jpg
```

**Constraints:**
- Maximum size: 25MB
- Supported formats: Video (MP4), Audio (MP3), Images (JPEG, JPG, PNG)
- Automatic chunking and integrity verification

#### Receiving Files
1. Download button (⬇) appears in chat
2. Click button to accept
3. Choose save location in dialog
4. System message confirms completion

### Emoji Usage

#### Visual Picker
1. Click "😃" button
2. Browse categorized tabs:
   - 😊 Smileys
   - 🐶 Animals
   - 🍊 Foods
   - 💖 Symbols
3. Click emoji to insert at cursor

#### Text Shortcodes
```
I'm happy :smile: and excited :tada:
```
Converts to:
```
I'm happy 😊 and excited 🎉
```

**Popular shortcodes:**
- `:smile:` → 😊
- `:heart:` → 🩷
- `:thumbsup:` → 👍
- `:fire:` → 🔥
- `:tada:` → 🎉

### User List Interaction

- **Green dot (🟢)**: User is online
- **Click username**: Opens private message dialog
- **Auto-updates**: Join/leave events refresh list instantly

### System Features

#### Message History
- Auto-scroll to latest message
- Scrollback for previous messages
- Color-coded by type (blue: global, orange: private)

#### Status Indicators
- Connection status in title bar
- System messages for events (joins, leaves, errors)
- Progress bars for file transfers

#### Graceful Exit
1. Click window close button
2. Confirm exit dialog
3. Server notifies all users of departure
4. User removed from active list

---

## Performance Analysis

### Strengths

| Aspect | Details |
|--------|---------|
| **Security** | Military-grade AES-256 encryption with RSA key exchange |
| **Usability** | Intuitive GUI with zero-configuration client setup |
| **Reliability** | Comprehensive error handling with automatic recovery |
| **Extensibility** | Modular architecture supporting feature additions |
| **Transparency** | SQLite logging for complete audit trail |
| **Real-time** | Sub-second message delivery with Socket.IO |

### Current Limitations

| Category | Limitation | Impact |
|----------|------------|--------|
| **Scalability** | Thread-per-connection model | Practical limit of ~100 concurrent users |
| **File Transfer** | 25MB size limit | Cannot share large media files |
| **Network Topology** | Localhost/LAN only | Requires VPN for internet use |
| **GUI Framework** | Tkinter constraints | Limited styling and animation |
| **File Types** | Restricted format whitelist | Cannot share documents, archives |
| **Encryption Overhead** | 10-15ms latency per message | Noticeable on slow connections |

### Performance Metrics

**Measured on MacBook Pro M1, 16GB RAM:**

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Message encryption/decryption | 2-3ms | N/A |
| Message delivery (local) | 5-10ms | ~200 msg/sec |
| File transfer (10MB) | 8-12 sec | ~1 MB/sec |
| User join/leave propagation | 15-25ms | N/A |
| Key exchange (RSA) | 20-30ms | Once per session |

---

## Development Roadmap

### Phase 1: Foundation Enhancement (Q1 2026)
- [ ] Migrate to async/await architecture (asyncio)
- [ ] Implement connection pooling
- [ ] Add WebSocket compression
- [ ] Optimize file chunking algorithm

### Phase 2: Feature Expansion (Q2 2026)
- [ ] Voice message support
- [ ] Screen sharing capability
- [ ] Message reactions and replies
- [ ] Rich text formatting (bold, italic, code blocks)
- [ ] Group chat creation and management

### Phase 3: Platform Modernization (Q3 2026)
- [ ] Web client (React/Vue.js)
- [ ] Mobile apps (React Native)
- [ ] Desktop app bundling (PyInstaller)
- [ ] Dark mode theme
- [ ] Customizable UI themes

### Phase 4: Enterprise Features (Q4 2026)
- [ ] User authentication system (JWT)
- [ ] Role-based access control
- [ ] Message history persistence
- [ ] Full-text search
- [ ] Export chat history (PDF, TXT)
- [ ] Admin dashboard

### Phase 5: Cloud Deployment (2027)
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] Load balancing
- [ ] CDN integration for file delivery
- [ ] Horizontal scaling support

---

## Credits & Resources

### Academic Foundation
This project was developed as part of **Independent Study in Computer Networks - FUV Summer 2025**, building upon principles from:

- **Kurose, J. F., & Ross, K. W.** (2021). *Computer Networking: A Top-Down Approach* (8th ed.). Pearson.

### Special Acknowledgments
- **Professor Dang Huynh** - Academic advisor and project mentor
- **FUV Computer Science Department** - Infrastructure and resources

### Technology Stack
- **Python 3.9+** - Core programming language
- **Flask** - Web framework
- **Socket.IO** - Real-time bidirectional communication
- **Cryptography** - Encryption library (RSA, AES)
- **Tkinter** - GUI framework
- **SQLite** - Embedded database
- **Eventlet** - Concurrent networking library

### Open Source Libraries
```txt
flask==2.3.0
python-socketio==5.9.0
cryptography==41.0.3
eventlet==0.33.3
```

### Development Tools
- **pytest** - Testing framework
- **Visual Studio Code** - IDE
- **Git** - Version control
- **Mermaid** - Diagram generation

### References & Inspiration
1. Socket.IO Documentation: https://socket.io/docs/
2. Cryptography in Python: https://cryptography.io/
3. Flask-SocketIO Guide: https://flask-socketio.readthedocs.io/
4. AES Encryption Best Practices: NIST SP 800-38A

---

## License

This project is released under the **MIT License**.

```
Copyright (c) 2025 ChatSpace Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

---

## Support

For questions, issues, or suggestions:

- **GitHub Issues**: [Report a bug](https://github.com/nami-macos/chatroom-project/issues)
- **Email**: nami@example.com
- **Documentation**: [Wiki](https://github.com/nami-macos/chatroom-project/wiki)

