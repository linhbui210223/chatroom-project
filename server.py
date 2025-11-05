#!/usr/bin/env python3
"""
Secure Multi-User Chat Server
Handles multiple client connections, message routing, file sharing, and user management.
"""

import socket
import threading
import json
import os
import base64
from datetime import datetime
from cryptography.fernet import Fernet

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {client_socket: {'username': str, 'cipher': Fernet}}
        self.usernames = {}  # {username: client_socket}
        self.clients_lock = threading.Lock()
        self.running = False
        
        # Generate server encryption key
        self.server_key = Fernet.generate_key()
        self.server_cipher = Fernet(self.server_key)
        
        # Create uploads directory for file sharing
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
    
    def start(self):
        """Start the chat server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"[SERVER] Server started on {self.host}:{self.port}")
        print(f"[SERVER] Encryption key: {self.server_key.decode()}")
        
        # Accept clients in a loop
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[SERVER] New connection from {address}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Error accepting connection: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle communication with a specific client."""
        try:
            # First, send the encryption key to the client
            client_socket.send(self.server_key)
            
            # Receive username
            username_data = client_socket.recv(1024)
            username = self.server_cipher.decrypt(username_data).decode()
            
            # Check if username is already taken
            with self.clients_lock:
                if username in self.usernames:
                    error_msg = self.server_cipher.encrypt(b"USERNAME_TAKEN")
                    client_socket.send(error_msg)
                    client_socket.close()
                    return
                
                # Register the client
                self.clients[client_socket] = {
                    'username': username,
                    'cipher': self.server_cipher,
                    'address': address
                }
                self.usernames[username] = client_socket
            
            # Send success confirmation
            success_msg = self.server_cipher.encrypt(b"USERNAME_ACCEPTED")
            client_socket.send(success_msg)
            
            print(f"[SERVER] User '{username}' connected from {address}")
            
            # Broadcast user joined message
            self.broadcast_message(f"[SERVER] {username} joined the chat!", exclude_socket=client_socket)
            
            # Send list of online users to the new client
            self.send_online_users(client_socket)
            
            # Handle messages from this client
            while self.running:
                try:
                    encrypted_data = client_socket.recv(4096)
                    if not encrypted_data:
                        break
                    
                    # Decrypt the message
                    decrypted_data = self.server_cipher.decrypt(encrypted_data)
                    message_data = json.loads(decrypted_data.decode())
                    
                    self.process_message(client_socket, message_data)
                    
                except Exception as e:
                    print(f"[ERROR] Error handling message from {username}: {e}")
                    break
        
        except Exception as e:
            print(f"[ERROR] Error in client handler for {address}: {e}")
        
        finally:
            self.disconnect_client(client_socket)
    
    def process_message(self, client_socket, message_data):
        """Process different types of messages."""
        msg_type = message_data.get('type')
        
        if msg_type == 'broadcast':
            # Broadcast message to all clients
            username = self.clients[client_socket]['username']
            content = message_data.get('content', '')
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_msg = f"[{timestamp}] {username}: {content}"
            self.broadcast_message(formatted_msg)
            
        elif msg_type == 'private':
            # Private message to specific user
            username = self.clients[client_socket]['username']
            recipient = message_data.get('recipient')
            content = message_data.get('content', '')
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_msg = f"[{timestamp}] [PRIVATE from {username}]: {content}"
            self.send_private_message(username, recipient, formatted_msg)
            
        elif msg_type == 'file':
            # Handle file transfer
            self.handle_file_transfer(client_socket, message_data)
        
        elif msg_type == 'user_list':
            # Send updated user list
            self.send_online_users(client_socket)
    
    def handle_file_transfer(self, sender_socket, message_data):
        """Handle file transfer between users."""
        username = self.clients[sender_socket]['username']
        recipient = message_data.get('recipient')
        filename = message_data.get('filename')
        file_data = message_data.get('data')
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if recipient == 'all':
            # Broadcast file to all users
            file_msg = {
                'type': 'file',
                'sender': username,
                'filename': filename,
                'data': file_data,
                'timestamp': timestamp
            }
            self.broadcast_json(file_msg, exclude_socket=sender_socket)
            
            # Send confirmation to sender
            confirm_msg = f"[{timestamp}] File '{filename}' sent to all users"
            self.send_to_client(sender_socket, confirm_msg)
        else:
            # Send file to specific user
            with self.clients_lock:
                if recipient in self.usernames:
                    recipient_socket = self.usernames[recipient]
                else:
                    recipient_socket = None
            
            if recipient_socket:
                file_msg = {
                    'type': 'file',
                    'sender': username,
                    'filename': filename,
                    'data': file_data,
                    'timestamp': timestamp,
                    'private': True
                }
                self.send_json_to_client(recipient_socket, file_msg)
                
                # Send confirmation to sender
                confirm_msg = f"[{timestamp}] File '{filename}' sent to {recipient}"
                self.send_to_client(sender_socket, confirm_msg)
            else:
                # Recipient not found
                error_msg = f"[{timestamp}] User '{recipient}' not found"
                self.send_to_client(sender_socket, error_msg)
    
    def broadcast_message(self, message, exclude_socket=None):
        """Broadcast a text message to all connected clients."""
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                if client_socket != exclude_socket:
                    try:
                        self.send_to_client(client_socket, message)
                    except Exception as e:
                        print(f"[ERROR] Failed to send to client: {e}")
    
    def broadcast_json(self, data, exclude_socket=None):
        """Broadcast JSON data to all connected clients."""
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                if client_socket != exclude_socket:
                    try:
                        self.send_json_to_client(client_socket, data)
                    except Exception as e:
                        print(f"[ERROR] Failed to send to client: {e}")
    
    def send_to_client(self, client_socket, message):
        """Send a text message to a specific client."""
        message_data = {'type': 'message', 'content': message}
        self.send_json_to_client(client_socket, message_data)
    
    def send_json_to_client(self, client_socket, data):
        """Send JSON data to a specific client."""
        try:
            cipher = self.clients[client_socket]['cipher']
            json_data = json.dumps(data).encode()
            encrypted_data = cipher.encrypt(json_data)
            client_socket.send(encrypted_data)
        except Exception as e:
            print(f"[ERROR] Failed to send JSON to client: {e}")
    
    def send_private_message(self, sender, recipient, message):
        """Send a private message to a specific user."""
        with self.clients_lock:
            if recipient in self.usernames:
                recipient_socket = self.usernames[recipient]
                self.send_to_client(recipient_socket, message)
                
                # Send confirmation to sender
                sender_socket = self.usernames[sender]
                confirm_msg = f"[{datetime.now().strftime('%H:%M:%S')}] [PRIVATE to {recipient}]: {message.split(': ', 1)[-1]}"
                self.send_to_client(sender_socket, confirm_msg)
            else:
                # User not found
                sender_socket = self.usernames.get(sender)
                if sender_socket:
                    error_msg = f"[SERVER] User '{recipient}' not found"
                    self.send_to_client(sender_socket, error_msg)
    
    def send_online_users(self, client_socket):
        """Send list of online users to a client."""
        with self.clients_lock:
            users_list = list(self.usernames.keys())
        
        user_data = {
            'type': 'user_list',
            'users': users_list
        }
        self.send_json_to_client(client_socket, user_data)
    
    def disconnect_client(self, client_socket):
        """Disconnect a client and clean up."""
        with self.clients_lock:
            if client_socket in self.clients:
                username = self.clients[client_socket]['username']
                del self.clients[client_socket]
                del self.usernames[username]
                
                print(f"[SERVER] User '{username}' disconnected")
                
                # Broadcast user left message
                self.broadcast_message(f"[SERVER] {username} left the chat")
                
                # Broadcast updated user list
                self.broadcast_user_list()
        
        try:
            client_socket.close()
        except:
            pass
    
    def broadcast_user_list(self):
        """Broadcast updated user list to all clients."""
        with self.clients_lock:
            users_list = list(self.usernames.keys())
        
        user_data = {
            'type': 'user_list',
            'users': users_list
        }
        self.broadcast_json(user_data)
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[SERVER] Server stopped")

def main():
    """Main function to start the server."""
    server = ChatServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down server...")
        server.stop()
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        server.stop()

if __name__ == "__main__":
    main()
