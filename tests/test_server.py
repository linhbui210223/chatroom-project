import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestChatServer:
    @pytest.fixture
    def chat_server(self):
        """Create a ChatServer instance for testing"""
        with patch('server.server.load_rsa_private_key'):
            from server.server import ChatServer  # Import here to avoid issues
            server = ChatServer()
            server.private_key = Mock()
            return server

    def test_server_initialization(self, chat_server):
        """Test server initializes correctly"""
        assert chat_server.users == []
        assert hasattr(chat_server, 'aes_keys')
        assert hasattr(chat_server, 'upload_files')
        print("✅ Server initialization test passed")

    def test_user_management(self, chat_server):
        """Test basic user management"""
        # Add a user
        test_user = {'sid': 'test123', 'username': 'testuser', 'aes_key': b'testkey'}
        chat_server.users.append(test_user)
        
        assert len(chat_server.users) == 1
        assert chat_server.users[0]['username'] == 'testuser'
        print("✅ User management test passed")

    def test_user_lookup(self, chat_server):
        """Test finding users by sid"""
        # Add test users
        chat_server.users = [
            {'sid': 'sid1', 'username': 'user1', 'aes_key': b'key1'},
            {'sid': 'sid2', 'username': 'user2', 'aes_key': b'key2'}
        ]
        
        # Find user by sid
        user = next((u for u in chat_server.users if u['sid'] == 'sid1'), None)
        assert user is not None
        assert user['username'] == 'user1'
        print("✅ User lookup test passed")

# Add a simple standalone test function too
def test_simple_math():
    """Simple test to verify pytest is working"""
    assert 2 + 2 == 4
    print("✅ Simple math test passed")
    # Add project root to Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    class TestChatServer:
        @pytest.fixture
        def chat_server(self):
            """Create a ChatServer instance for testing"""
            with patch('server.server.load_rsa_private_key'):
                from server.server import ChatServer  # Import here to avoid issues
                server = ChatServer()
                server.private_key = Mock()
                return server

        def test_server_initialization(self, chat_server):
            """Test server initializes correctly"""
            assert chat_server.users == []
            assert hasattr(chat_server, 'aes_keys')
            assert hasattr(chat_server, 'upload_files')
            print("✅ Server initialization test passed")

        def test_user_management(self, chat_server):
            """Test basic user management"""
            # Add a user
            test_user = {'sid': 'test123', 'username': 'testuser', 'aes_key': b'testkey'}
            chat_server.users.append(test_user)
            
            assert len(chat_server.users) == 1
            assert chat_server.users[0]['username'] == 'testuser'
            print("✅ User management test passed")

        def test_user_lookup(self, chat_server):
            """Test finding users by sid"""
            # Add test users
            chat_server.users = [
                {'sid': 'sid1', 'username': 'user1', 'aes_key': b'key1'},
                {'sid': 'sid2', 'username': 'user2', 'aes_key': b'key2'}
            ]
            
            # Find user by sid
            user = next((u for u in chat_server.users if u['sid'] == 'sid1'), None)
            assert user is not None
            assert user['username'] == 'user1'
            print("✅ User lookup test passed")

        def test_connect_event(self, chat_server):
            """Test the connect event"""
            with patch('server.server.log_event') as mock_log_event:
                chat_server.sio.handlers['message']['connect']('test_sid', {})
                mock_log_event.assert_called_with("server", "connect", "Client test_sid connected.")
                print("✅ Connect event test passed")

        def test_disconnect_event(self, chat_server):
            """Test the disconnect event"""
            chat_server.users = [{'sid': 'test_sid', 'username': 'testuser', 'aes_key': b'testkey'}]
            with patch('server.server.log_event') as mock_log_event:
                chat_server.sio.handlers['message']['disconnect']('test_sid')
                assert len(chat_server.users) == 0
                mock_log_event.assert_called_with("server", "disconnect", "User testuser disconnected (test_sid)")
                print("✅ Disconnect event test passed")

        def test_exchange_key_event(self, chat_server):
            """Test the exchange_key event"""
            with patch('server.server.decrypt_rsa', return_value=b'test_aes_key') as mock_decrypt_rsa, \
                 patch('server.server.log_event') as mock_log_event:
                data = {'encrypted_aes': base64.b64encode(b'encrypted_key').decode()}
                chat_server.sio.handlers['message']['exchange_key']('test_sid', data)
                assert chat_server.aes_keys['test_sid'] == b'test_aes_key'
                mock_decrypt_rsa.assert_called_once()
                mock_log_event.assert_called_with("server", "exchange_key", "[Key Exchange] AES key received for client test_sid")
                print("✅ Exchange key event test passed")

        def test_user_joined_event(self, chat_server):
            """Test the user_joined event"""
            chat_server.aes_keys['test_sid'] = b'test_aes_key'
            with patch('server.server.log_event') as mock_log_event:
                data = {'username': 'testuser'}
                chat_server.sio.handlers['message']['user_joined']('test_sid', data)
                assert len(chat_server.users) == 1
                assert chat_server.users[0]['username'] == 'testuser'
                mock_log_event.assert_called_with("server", "user_joined", "User 'testuser' joined (SID: test_sid)")
                print("✅ User joined event test passed")

        def test_global_message_event(self, chat_server):
            """Test the global_message event"""
            chat_server.users = [{'sid': 'test_sid', 'username': 'testuser', 'aes_key': b'testkey'}]
            with patch('server.server.decrypt_aes', return_value='Hello, world!') as mock_decrypt_aes, \
                 patch('server.server.encrypt_aes', return_value='encrypted_message') as mock_encrypt_aes, \
                 patch('server.server.log_event') as mock_log_event:
                data = {'sender': 'testuser', 'message': 'encrypted_message'}
                chat_server.sio.handlers['message']['global_message']('test_sid', data)
                mock_decrypt_aes.assert_called_once()
                mock_encrypt_aes.assert_called_once()
                mock_log_event.assert_called_with("server", "global_msg", "[GLOBAL] From testuser: encrypted_message")
                print("✅ Global message event test passed")

        def test_private_message_event(self, chat_server):
            """Test the private_message event"""
            chat_server.users = [
                {'sid': 'sender_sid', 'username': 'sender', 'aes_key': b'sender_key'},
                {'sid': 'recipient_sid', 'username': 'recipient', 'aes_key': b'recipient_key'}
            ]
            with patch('server.server.decrypt_aes', return_value='Hello, recipient!') as mock_decrypt_aes, \
                 patch('server.server.encrypt_aes', return_value='encrypted_message') as mock_encrypt_aes, \
                 patch('server.server.log_event') as mock_log_event:
                data = {'sender': 'sender', 'recipient': 'recipient', 'message': 'encrypted_message'}
                chat_server.sio.handlers['message']['private_message']('sender_sid', data)
                mock_decrypt_aes.assert_called_once()
                mock_encrypt_aes.assert_called_once()
                mock_log_event.assert_called_with("server", "private_msg", "[PRIVATE] From sender to recipient: encrypted_message")
                print("Private message event test passed")

    # Add a simple standalone test function too
    def test_simple_math():
        """Simple test to verify pytest is working"""
        assert 2 + 2 == 4
        print("Simple math test passed")
