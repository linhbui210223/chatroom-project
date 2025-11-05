#!/usr/bin/env python3
"""
Secure Multi-User Chat Client
GUI-based chat client with encryption, private messaging, file sharing, and emoji support.
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
import base64
from cryptography.fernet import Fernet
import emoji

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client_socket = None
        self.cipher = None
        self.username = None
        self.running = False
        
        # GUI components
        self.root = None
        self.chat_display = None
        self.message_entry = None
        self.user_listbox = None
        self.recipient_var = None
        
    def connect_to_server(self, username):
        """Connect to the chat server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Receive encryption key from server
            encryption_key = self.client_socket.recv(1024)
            self.cipher = Fernet(encryption_key)
            
            # Send username
            encrypted_username = self.cipher.encrypt(username.encode())
            self.client_socket.send(encrypted_username)
            
            # Wait for confirmation
            response_data = self.client_socket.recv(1024)
            response = self.cipher.decrypt(response_data).decode()
            
            if response == "USERNAME_TAKEN":
                return False, "Username already taken"
            elif response == "USERNAME_ACCEPTED":
                self.username = username
                self.running = True
                
                # Start receiving messages in a separate thread
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                
                return True, "Connected successfully"
            
        except Exception as e:
            return False, f"Connection error: {e}"
    
    def receive_messages(self):
        """Receive and process messages from the server."""
        while self.running:
            try:
                encrypted_data = self.client_socket.recv(4096)
                if not encrypted_data:
                    break
                
                # Decrypt the message
                decrypted_data = self.cipher.decrypt(encrypted_data)
                message_data = json.loads(decrypted_data.decode())
                
                self.process_received_message(message_data)
                
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Error receiving message: {e}")
                    self.display_message("[ERROR] Connection lost to server")
                break
        
        self.disconnect()
    
    def process_received_message(self, message_data):
        """Process different types of received messages."""
        msg_type = message_data.get('type')
        
        if msg_type == 'message':
            # Display text message
            content = message_data.get('content', '')
            # Support emoji rendering
            content = emoji.emojize(content, language='alias')
            self.display_message(content)
            
        elif msg_type == 'file':
            # Handle received file
            sender = message_data.get('sender')
            filename = message_data.get('filename')
            file_data = message_data.get('data')
            timestamp = message_data.get('timestamp')
            is_private = message_data.get('private', False)
            
            msg_prefix = "[PRIVATE] " if is_private else ""
            self.display_message(f"[{timestamp}] {msg_prefix}File received from {sender}: {filename}")
            
            # Ask user if they want to save the file
            self.root.after(0, lambda: self.prompt_save_file(filename, file_data))
            
        elif msg_type == 'user_list':
            # Update online users list
            users = message_data.get('users', [])
            self.update_user_list(users)
    
    def send_message(self, content, recipient='all'):
        """Send a message to the server."""
        try:
            if recipient == 'all':
                message_data = {
                    'type': 'broadcast',
                    'content': content
                }
            else:
                message_data = {
                    'type': 'private',
                    'recipient': recipient,
                    'content': content
                }
            
            # Encrypt and send
            json_data = json.dumps(message_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            self.client_socket.send(encrypted_data)
            
        except Exception as e:
            self.display_message(f"[ERROR] Failed to send message: {e}")
    
    def send_file(self, filepath, recipient='all'):
        """Send a file to the server."""
        try:
            filename = os.path.basename(filepath)
            
            # Read file and encode to base64
            with open(filepath, 'rb') as f:
                file_bytes = f.read()
                file_data = base64.b64encode(file_bytes).decode()
            
            message_data = {
                'type': 'file',
                'recipient': recipient,
                'filename': filename,
                'data': file_data
            }
            
            # Encrypt and send
            json_data = json.dumps(message_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            self.client_socket.send(encrypted_data)
            
        except Exception as e:
            self.display_message(f"[ERROR] Failed to send file: {e}")
    
    def disconnect(self):
        """Disconnect from the server."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        if self.root:
            self.root.after(0, lambda: self.display_message("[DISCONNECTED] Connection closed"))
    
    def display_message(self, message):
        """Display a message in the chat window."""
        if self.chat_display:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, message + "\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
    
    def update_user_list(self, users):
        """Update the online users listbox."""
        if self.user_listbox:
            self.user_listbox.delete(0, tk.END)
            self.user_listbox.insert(tk.END, "All Users")
            for user in users:
                if user != self.username:
                    self.user_listbox.insert(tk.END, user)
    
    def prompt_save_file(self, filename, file_data):
        """Prompt user to save a received file."""
        save = messagebox.askyesno("File Received", f"Save file '{filename}'?")
        if save:
            save_path = filedialog.asksaveasfilename(
                initialfile=filename,
                defaultextension=os.path.splitext(filename)[1]
            )
            if save_path:
                try:
                    file_bytes = base64.b64decode(file_data)
                    with open(save_path, 'wb') as f:
                        f.write(file_bytes)
                    self.display_message(f"[INFO] File saved to: {save_path}")
                except Exception as e:
                    self.display_message(f"[ERROR] Failed to save file: {e}")
    
    def create_gui(self):
        """Create the GUI for the chat client."""
        self.root = tk.Tk()
        self.root.title(f"Secure Chat - {self.username}")
        self.root.geometry("800x600")
        
        # Create main container with paned window
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Chat area
        left_frame = tk.Frame(main_paned)
        main_paned.add(left_frame, stretch="always")
        
        # Chat display area
        chat_label = tk.Label(left_frame, text="Chat Messages", font=("Arial", 10, "bold"))
        chat_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.chat_display = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("Arial", 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Message input area
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        message_label = tk.Label(input_frame, text="Message:", font=("Arial", 9))
        message_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.message_entry = tk.Entry(input_frame, font=("Arial", 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", self.on_send_message)
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.on_send_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold")
        )
        send_button.pack(side=tk.LEFT, padx=(0, 5))
        
        emoji_button = tk.Button(
            input_frame,
            text="😀",
            command=self.insert_emoji,
            font=("Arial", 10)
        )
        emoji_button.pack(side=tk.LEFT, padx=(0, 5))
        
        file_button = tk.Button(
            input_frame,
            text="📎 File",
            command=self.on_send_file,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold")
        )
        file_button.pack(side=tk.LEFT)
        
        # Right panel - Users list
        right_frame = tk.Frame(main_paned, width=200)
        main_paned.add(right_frame)
        
        users_label = tk.Label(right_frame, text="Online Users", font=("Arial", 10, "bold"))
        users_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.user_listbox = tk.Listbox(right_frame, font=("Arial", 10))
        self.user_listbox.pack(fill=tk.BOTH, expand=True)
        self.user_listbox.insert(tk.END, "All Users")
        
        # Status bar
        status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = tk.Label(
            status_frame,
            text=f"Connected as: {self.username} | Server: {self.host}:{self.port}",
            anchor=tk.W,
            font=("Arial", 8)
        )
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Welcome message
        self.display_message("=== Welcome to Secure Chat ===")
        self.display_message("Connected to server with end-to-end encryption")
        self.display_message("Select 'All Users' to broadcast or select a user for private message")
        self.display_message("Emoji support enabled! Use :smile:, :heart:, :thumbsup:, etc.")
        self.display_message("=" * 50)
        
        self.root.mainloop()
    
    def on_send_message(self, event=None):
        """Handle send button click."""
        message = self.message_entry.get().strip()
        if message:
            # Get selected recipient
            selection = self.user_listbox.curselection()
            if selection:
                selected_user = self.user_listbox.get(selection[0])
                recipient = 'all' if selected_user == 'All Users' else selected_user
            else:
                recipient = 'all'
            
            # Convert emoji aliases to unicode
            message = emoji.emojize(message, language='alias')
            
            self.send_message(message, recipient)
            self.message_entry.delete(0, tk.END)
    
    def on_send_file(self):
        """Handle file send button click."""
        filepath = filedialog.askopenfilename(title="Select file to send")
        if filepath:
            # Check file size (limit to 10MB)
            file_size = os.path.getsize(filepath)
            if file_size > 10 * 1024 * 1024:
                messagebox.showwarning("File Too Large", "File size must be less than 10MB")
                return
            
            # Get selected recipient
            selection = self.user_listbox.curselection()
            if selection:
                selected_user = self.user_listbox.get(selection[0])
                recipient = 'all' if selected_user == 'All Users' else selected_user
            else:
                recipient = 'all'
            
            self.send_file(filepath, recipient)
            self.display_message(f"[INFO] Sending file: {os.path.basename(filepath)}")
    
    def insert_emoji(self):
        """Insert common emojis."""
        emoji_window = tk.Toplevel(self.root)
        emoji_window.title("Select Emoji")
        emoji_window.geometry("300x200")
        
        # Common emoji shortcuts
        emojis = [
            ("😀", ":smile:"), ("😂", ":joy:"), ("❤️", ":heart:"),
            ("👍", ":thumbsup:"), ("👎", ":thumbsdown:"), ("😊", ":blush:"),
            ("😎", ":sunglasses:"), ("🎉", ":tada:"), ("🔥", ":fire:"),
            ("✅", ":white_check_mark:"), ("❌", ":x:"), ("💯", ":100:")
        ]
        
        row, col = 0, 0
        for emoji_char, emoji_code in emojis:
            btn = tk.Button(
                emoji_window,
                text=emoji_char,
                font=("Arial", 20),
                command=lambda e=emoji_code: self.insert_emoji_text(e, emoji_window)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(4):
            emoji_window.grid_columnconfigure(i, weight=1)
        for i in range(3):
            emoji_window.grid_rowconfigure(i, weight=1)
    
    def insert_emoji_text(self, emoji_code, window):
        """Insert emoji code into message entry."""
        current_text = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, current_text + emoji_code)
        window.destroy()
        self.message_entry.focus()
    
    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.disconnect()
            self.root.destroy()

def login_window():
    """Create login window to get username and server details."""
    login_root = tk.Tk()
    login_root.title("Secure Chat - Login")
    login_root.geometry("400x250")
    login_root.resizable(False, False)
    
    result = {'username': None, 'host': '127.0.0.1', 'port': 5555, 'connect': False}
    
    # Title
    title_label = tk.Label(
        login_root,
        text="Secure Multi-User Chat",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=20)
    
    # Username
    username_frame = tk.Frame(login_root)
    username_frame.pack(pady=10)
    
    username_label = tk.Label(username_frame, text="Username:", font=("Arial", 10))
    username_label.pack(side=tk.LEFT, padx=5)
    
    username_entry = tk.Entry(username_frame, font=("Arial", 10), width=20)
    username_entry.pack(side=tk.LEFT, padx=5)
    username_entry.focus()
    
    # Server host
    host_frame = tk.Frame(login_root)
    host_frame.pack(pady=5)
    
    host_label = tk.Label(host_frame, text="Server Host:", font=("Arial", 10))
    host_label.pack(side=tk.LEFT, padx=5)
    
    host_entry = tk.Entry(host_frame, font=("Arial", 10), width=20)
    host_entry.insert(0, "127.0.0.1")
    host_entry.pack(side=tk.LEFT, padx=5)
    
    # Server port
    port_frame = tk.Frame(login_root)
    port_frame.pack(pady=5)
    
    port_label = tk.Label(port_frame, text="Server Port:", font=("Arial", 10))
    port_label.pack(side=tk.LEFT, padx=5)
    
    port_entry = tk.Entry(port_frame, font=("Arial", 10), width=20)
    port_entry.insert(0, "5555")
    port_entry.pack(side=tk.LEFT, padx=5)
    
    def on_connect():
        username = username_entry.get().strip()
        host = host_entry.get().strip()
        port_str = port_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        if not host:
            messagebox.showerror("Error", "Please enter server host")
            return
        
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        result['username'] = username
        result['host'] = host
        result['port'] = port
        result['connect'] = True
        login_root.destroy()
    
    # Connect button
    connect_button = tk.Button(
        login_root,
        text="Connect",
        command=on_connect,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15
    )
    connect_button.pack(pady=20)
    
    # Bind Enter key
    username_entry.bind("<Return>", lambda e: on_connect())
    host_entry.bind("<Return>", lambda e: on_connect())
    port_entry.bind("<Return>", lambda e: on_connect())
    
    login_root.mainloop()
    return result

def main():
    """Main function to start the client."""
    # Show login window
    login_info = login_window()
    
    if not login_info['connect']:
        return
    
    # Create client
    client = ChatClient(login_info['host'], login_info['port'])
    
    # Connect to server
    success, message = client.connect_to_server(login_info['username'])
    
    if success:
        # Start GUI
        client.create_gui()
    else:
        # Show error
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Connection Error", message)
        error_root.destroy()

if __name__ == "__main__":
    main()
