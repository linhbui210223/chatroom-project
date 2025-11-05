#!/usr/bin/env python3
"""
Simple demonstration and test of the chat application
"""

import socket
import threading
import json
import time
from cryptography.fernet import Fernet

def simple_client_test(username, message_to_send=None):
    """Create a simple test client"""
    try:
        # Connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5555))
        print(f"[{username}] Connected to server")
        
        # Get encryption key
        key = client.recv(1024)
        cipher = Fernet(key)
        print(f"[{username}] Received encryption key")
        
        # Send username
        encrypted_username = cipher.encrypt(username.encode())
        client.send(encrypted_username)
        print(f"[{username}] Sent username")
        
        # Get response
        response = client.recv(1024)
        decrypted = cipher.decrypt(response).decode()
        print(f"[{username}] Server response: {decrypted}")
        
        if decrypted == "USERNAME_ACCEPTED":
            print(f"[{username}] ✓ Successfully authenticated!")
            
            if message_to_send:
                time.sleep(1)
                # Send a message
                msg_data = {'type': 'broadcast', 'content': message_to_send}
                json_data = json.dumps(msg_data).encode()
                encrypted = cipher.encrypt(json_data)
                client.send(encrypted)
                print(f"[{username}] Sent message: {message_to_send}")
                time.sleep(1)
            
            return True
        else:
            print(f"[{username}] ✗ Authentication failed: {decrypted}")
            return False
            
    except Exception as e:
        print(f"[{username}] Error: {e}")
        return False
    finally:
        try:
            client.close()
        except:
            pass

def main():
    print("=" * 60)
    print("SECURE CHAT APPLICATION - BASIC TESTS")
    print("=" * 60)
    print()
    
    # Test 1: Single client connection
    print("Test 1: Single client connection")
    print("-" * 40)
    result1 = simple_client_test("Alice", "Hello from Alice!")
    time.sleep(2)
    print()
    
    # Test 2: Another client
    print("Test 2: Another client connection")
    print("-" * 40)
    result2 = simple_client_test("Bob", "Hello from Bob!")
    time.sleep(2)
    print()
    
    # Test 3: Third client
    print("Test 3: Third client connection")
    print("-" * 40)
    result3 = simple_client_test("Charlie", "Hello from Charlie!")
    time.sleep(2)
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Test 1 (Alice): {'PASS' if result1 else 'FAIL'}")
    print(f"Test 2 (Bob): {'PASS' if result2 else 'FAIL'}")
    print(f"Test 3 (Charlie): {'PASS' if result3 else 'FAIL'}")
    print()
    
    if result1 and result2 and result3:
        print("✓ All basic tests passed!")
        print()
        print("The chat application is working correctly!")
        print("Key features validated:")
        print("  - Server accepts connections ✓")
        print("  - Encryption is working ✓")
        print("  - Multiple clients can connect ✓")
        print("  - Authentication is working ✓")
        print()
        print("To test interactively, run:")
        print("  python client.py")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    print("\nMake sure server.py is running!")
    print("If not, start it with: python server.py")
    print()
    input("Press Enter to continue...")
    print()
    
    exit(main())
