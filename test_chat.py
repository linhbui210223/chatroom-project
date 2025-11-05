#!/usr/bin/env python3
"""
Test script for the secure chat application
Tests server functionality, encryption, message routing, and file transfer
"""

import socket
import threading
import json
import time
import base64
from cryptography.fernet import Fernet

class TestClient:
    """Simple test client for automated testing"""
    
    def __init__(self, username, host='127.0.0.1', port=5555):
        self.username = username
        self.host = host
        self.port = port
        self.client_socket = None
        self.cipher = None
        self.received_messages = []
        self.running = False
        
    def connect(self):
        """Connect to server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Receive encryption key
            encryption_key = self.client_socket.recv(1024)
            self.cipher = Fernet(encryption_key)
            
            # Send username
            encrypted_username = self.cipher.encrypt(self.username.encode())
            self.client_socket.send(encrypted_username)
            
            # Wait for confirmation
            response_data = self.client_socket.recv(1024)
            response = self.cipher.decrypt(response_data).decode()
            
            if response == "USERNAME_ACCEPTED":
                self.running = True
                
                # Start receiving messages
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                
                return True
            return False
            
        except Exception as e:
            print(f"[TEST] Connection error for {self.username}: {e}")
            return False
    
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                encrypted_data = self.client_socket.recv(4096)
                if not encrypted_data:
                    break
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                message_data = json.loads(decrypted_data.decode())
                self.received_messages.append(message_data)
                
            except Exception as e:
                if self.running:
                    print(f"[TEST] Error receiving for {self.username}: {e}")
                break
    
    def send_message(self, content, recipient='all'):
        """Send a message"""
        try:
            if recipient == 'all':
                message_data = {'type': 'broadcast', 'content': content}
            else:
                message_data = {'type': 'private', 'recipient': recipient, 'content': content}
            
            json_data = json.dumps(message_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            self.client_socket.send(encrypted_data)
            return True
        except Exception as e:
            print(f"[TEST] Send error for {self.username}: {e}")
            return False
    
    def send_file(self, filename, data, recipient='all'):
        """Send a file"""
        try:
            file_data = base64.b64encode(data).decode()
            message_data = {
                'type': 'file',
                'recipient': recipient,
                'filename': filename,
                'data': file_data
            }
            
            json_data = json.dumps(message_data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            self.client_socket.send(encrypted_data)
            return True
        except Exception as e:
            print(f"[TEST] File send error for {self.username}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass

def test_server_connection():
    """Test 1: Server connection and authentication"""
    print("\n=== Test 1: Server Connection ===")
    
    client = TestClient("TestUser1")
    if client.connect():
        print("[PASS] Successfully connected to server")
        time.sleep(0.5)
        client.disconnect()
        return True
    else:
        print("[FAIL] Failed to connect to server")
        return False

def test_duplicate_username():
    """Test 2: Duplicate username rejection"""
    print("\n=== Test 2: Duplicate Username ===")
    
    client1 = TestClient("DuplicateUser")
    client2 = TestClient("DuplicateUser")
    
    if client1.connect():
        time.sleep(0.5)
        
        # Try to connect with same username
        if not client2.connect():
            print("[PASS] Duplicate username correctly rejected")
            client1.disconnect()
            return True
        else:
            print("[FAIL] Duplicate username was allowed")
            client1.disconnect()
            client2.disconnect()
            return False
    else:
        print("[FAIL] Could not establish first connection")
        return False

def test_broadcast_messaging():
    """Test 3: Broadcast messaging"""
    print("\n=== Test 3: Broadcast Messaging ===")
    
    client1 = TestClient("BroadcastUser1")
    client2 = TestClient("BroadcastUser2")
    
    if not (client1.connect() and client2.connect()):
        print("[FAIL] Could not connect clients")
        return False
    
    time.sleep(1)  # Wait for connections to settle
    
    # Clear any welcome messages
    client2.received_messages.clear()
    
    # Client1 sends broadcast message
    test_message = "Hello everyone!"
    client1.send_message(test_message)
    
    time.sleep(1)  # Wait for message delivery
    
    # Check if client2 received the message
    received = False
    for msg in client2.received_messages:
        if msg.get('type') == 'message':
            content = msg.get('content', '')
            if test_message in content and 'BroadcastUser1' in content:
                received = True
                break
    
    client1.disconnect()
    client2.disconnect()
    
    if received:
        print("[PASS] Broadcast message received successfully")
        return True
    else:
        print("[FAIL] Broadcast message not received")
        return False

def test_private_messaging():
    """Test 4: Private messaging"""
    print("\n=== Test 4: Private Messaging ===")
    
    client1 = TestClient("PrivateUser1")
    client2 = TestClient("PrivateUser2")
    client3 = TestClient("PrivateUser3")
    
    if not (client1.connect() and client2.connect() and client3.connect()):
        print("[FAIL] Could not connect clients")
        return False
    
    time.sleep(1)
    
    # Clear messages
    client2.received_messages.clear()
    client3.received_messages.clear()
    
    # Client1 sends private message to Client2
    test_message = "Private message for you"
    client1.send_message(test_message, recipient="PrivateUser2")
    
    time.sleep(1)
    
    # Check if client2 received it
    client2_received = False
    for msg in client2.received_messages:
        if msg.get('type') == 'message':
            content = msg.get('content', '')
            if 'PRIVATE' in content and test_message in content:
                client2_received = True
                break
    
    # Check if client3 did NOT receive it
    client3_received = False
    for msg in client3.received_messages:
        if msg.get('type') == 'message':
            content = msg.get('content', '')
            if test_message in content:
                client3_received = True
                break
    
    client1.disconnect()
    client2.disconnect()
    client3.disconnect()
    
    if client2_received and not client3_received:
        print("[PASS] Private message sent correctly")
        return True
    else:
        print("[FAIL] Private message routing failed")
        return False

def test_file_transfer():
    """Test 5: File transfer"""
    print("\n=== Test 5: File Transfer ===")
    
    client1 = TestClient("FileUser1")
    client2 = TestClient("FileUser2")
    
    if not (client1.connect() and client2.connect()):
        print("[FAIL] Could not connect clients")
        return False
    
    time.sleep(1)
    
    # Clear messages
    client2.received_messages.clear()
    
    # Client1 sends a file to all
    test_filename = "test_file.txt"
    test_data = b"This is test file content"
    client1.send_file(test_filename, test_data)
    
    time.sleep(1)
    
    # Check if client2 received the file
    file_received = False
    for msg in client2.received_messages:
        if msg.get('type') == 'file':
            if msg.get('filename') == test_filename:
                received_data = base64.b64decode(msg.get('data'))
                if received_data == test_data:
                    file_received = True
                    break
    
    client1.disconnect()
    client2.disconnect()
    
    if file_received:
        print("[PASS] File transfer successful")
        return True
    else:
        print("[FAIL] File transfer failed")
        return False

def test_multiple_clients():
    """Test 6: Multiple concurrent clients"""
    print("\n=== Test 6: Multiple Concurrent Clients ===")
    
    clients = []
    num_clients = 5
    
    # Connect multiple clients
    for i in range(num_clients):
        client = TestClient(f"MultiUser{i+1}")
        if client.connect():
            clients.append(client)
        else:
            print(f"[FAIL] Could not connect client {i+1}")
            for c in clients:
                c.disconnect()
            return False
    
    time.sleep(1)
    
    if len(clients) == num_clients:
        print(f"[PASS] {num_clients} clients connected successfully")
        
        # Disconnect all
        for client in clients:
            client.disconnect()
        
        return True
    else:
        print("[FAIL] Not all clients could connect")
        for client in clients:
            client.disconnect()
        return False

def test_encryption():
    """Test 7: Message encryption"""
    print("\n=== Test 7: Encryption ===")
    
    client = TestClient("EncryptionUser")
    
    if not client.connect():
        print("[FAIL] Could not connect client")
        return False
    
    time.sleep(0.5)
    
    # Verify cipher exists
    if client.cipher is not None:
        # Test encryption/decryption
        test_data = b"Test encryption message"
        encrypted = client.cipher.encrypt(test_data)
        decrypted = client.cipher.decrypt(encrypted)
        
        if decrypted == test_data:
            print("[PASS] Encryption/decryption working correctly")
            client.disconnect()
            return True
        else:
            print("[FAIL] Encryption/decryption failed")
            client.disconnect()
            return False
    else:
        print("[FAIL] No cipher established")
        client.disconnect()
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("SECURE CHAT APPLICATION - AUTOMATED TESTS")
    print("=" * 60)
    
    tests = [
        ("Server Connection", test_server_connection),
        ("Duplicate Username", test_duplicate_username),
        ("Broadcast Messaging", test_broadcast_messaging),
        ("Private Messaging", test_private_messaging),
        ("File Transfer", test_file_transfer),
        ("Multiple Clients", test_multiple_clients),
        ("Encryption", test_encryption),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Pause between tests
        except Exception as e:
            print(f"[ERROR] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    print("\nNOTE: Make sure the server is running before executing tests!")
    print("Start server with: python server.py\n")
    
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    
    if success:
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)
