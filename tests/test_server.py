import pytest
import sys
import os
import base64
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestChatServer:
    @pytest.fixture
    def chat_server(self):
        """Create a ChatServer instance for testing"""
        # ✅ FIXED: Patch the correct module path
        with patch('server.encryption.load_rsa_private_key', return_value=Mock()):
            from server.server import ChatServer
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
        test_user = {'sid': 'test123', 'username': 'testuser', 'aes_key': b'testkey'}
        chat_server.users.append(test_user)
        
        assert len(chat_server.users) == 1
        assert chat_server.users[0]['username'] == 'testuser'
        print("✅ User management test passed")

    def test_user_lookup(self, chat_server):
        """Test finding users by sid"""
        chat_server.users = [
            {'sid': 'sid1', 'username': 'user1', 'aes_key': b'key1'},
            {'sid': 'sid2', 'username': 'user2', 'aes_key': b'key2'}
        ]
        
        user = next((u for u in chat_server.users if u['sid'] == 'sid1'), None)
        assert user is not None
        assert user['username'] == 'user1'
        print("✅ User lookup test passed")

# Simple standalone test
def test_simple_math():
    """Simple test to verify pytest is working"""
    assert 2 + 2 == 4
    print("✅ Simple math test passed")