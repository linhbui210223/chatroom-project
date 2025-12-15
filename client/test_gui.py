import unittest
from unittest.mock import patch, MagicMock
from tkinter import Tk
from client.gui import ChatClientGUI

class TestChatClientGUI(unittest.TestCase):

    @patch("client.gui.tk.Tk")
    def setUp(self, mock_tk):
        """Set up the GUI instance for testing."""
        self.mock_tk = mock_tk
        self.gui = ChatClientGUI()

    def tearDown(self):
        """Destroy the GUI instance after each test."""
        self.gui.Window.destroy()

    @patch("client.gui.messagebox.showerror")
    @patch("client.gui.socketio.Client.connect")
    def test_connect_to_server_success(self, mock_connect, mock_showerror):
        """Test successful connection to the server."""
        mock_connect.return_value = None
        self.gui.connect_to_server()
        self.assertFalse(mock_showerror.called)

    @patch("client.gui.messagebox.showerror")
    @patch("client.gui.socketio.Client.connect")
    def test_connect_to_server_failure(self, mock_connect, mock_showerror):
        """Test failed connection to the server."""
        mock_connect.side_effect = Exception("Connection failed")
        self.gui.connect_to_server()
        mock_showerror.assert_called_once_with("Error", "Connection failed")

    @patch("client.gui.messagebox.showwarning")
    def test_validate_username_empty(self, mock_showwarning):
        """Test validation of an empty username."""
        result = self.gui.validate_username("")
        self.assertFalse(result)
        mock_showwarning.assert_called_once_with("Warning", "Please input a username.")

    @patch("client.gui.messagebox.showwarning")
    def test_validate_username_too_long(self, mock_showwarning):
        """Test validation of a username that is too long."""
        result = self.gui.validate_username("a" * 16)
        self.assertFalse(result)
        mock_showwarning.assert_called_once_with("Warning", "Username is too long. Please use a shorter username.")

    @patch("client.gui.messagebox.showwarning")
    def test_validate_username_with_spaces(self, mock_showwarning):
        """Test validation of a username with spaces."""
        result = self.gui.validate_username("user name")
        self.assertFalse(result)
        mock_showwarning.assert_called_once_with("Warning", "Username cannot contain spaces. Please choose another one.")

    @patch("client.gui.messagebox.showwarning")
    def test_validate_username_special_characters(self, mock_showwarning):
        """Test validation of a username with special characters."""
        result = self.gui.validate_username("user@name")
        self.assertFalse(result)
        mock_showwarning.assert_called_once_with("Warning", "Username cannot contain special characters. Please choose another one.")

    @patch("client.gui.messagebox.showwarning")
    @patch("client.gui.socketio.Client.call")
    def test_validate_username_already_taken(self, mock_call, mock_showwarning):
        """Test validation of a username that is already taken."""
        mock_call.return_value = {"current_usernames": ["existing_user"]}
        self.gui.active_users = ["existing_user"]
        result = self.gui.validate_username("existing_user")
        self.assertFalse(result)
        mock_showwarning.assert_called_once_with("Warning", "This username is already taken. Please choose another one.")

    @patch("client.gui.messagebox.showerror")
    def test_update_user_server_not_connected(self, mock_showerror):
        """Test updating the server with the username when not connected."""
        self.gui.sio.connected = False
        self.gui.update_user_server()
        mock_showerror.assert_called_once_with("Error", "Not connected to server.")

    @patch("client.gui.messagebox.showerror")
    @patch("client.gui.filedialog.askopenfilename")
    def test_select_file_invalid_path(self, mock_askopenfilename, mock_showerror):
        """Test selecting a file with an invalid path."""
        mock_askopenfilename.return_value = ""
        self.gui.select_file()
        self.assertFalse(mock_showerror.called)

    @patch("client.gui.messagebox.showwarning")
    @patch("client.gui.filedialog.askopenfilename")
    def test_select_file_large_file(self, mock_askopenfilename, mock_showwarning):
        """Test selecting a file that is too large."""
        mock_askopenfilename.return_value = "/path/to/large_file.mp4"
        with patch("os.path.getsize", return_value=30 * 1000 * 1000):  # 30 MB
            self.gui.select_file()
        mock_showwarning.assert_called_once_with("Warning", "Please choose a file smaller than 20 MB.")

    @patch("client.gui.messagebox.showwarning")
    @patch("client.gui.filedialog.askopenfilename")
    def test_select_file_invalid_extension(self, mock_askopenfilename, mock_showwarning):
        """Test selecting a file with an invalid extension."""
        mock_askopenfilename.return_value = "/path/to/file.txt"
        with patch("os.path.getsize", return_value=10 * 1000 * 1000):  # 10 MB
            self.gui.select_file()
        mock_showwarning.assert_called_once_with("Warning", "Inappropriate file type (not video, image, or audio)")

    @patch("client.gui.messagebox.askyesno")
    @patch("client.gui.filedialog.asksaveasfilename")
    def test_ask_download_decline(self, mock_asksaveasfilename, mock_askyesno):
        """Test declining a file download."""
        mock_askyesno.return_value = False
        self.gui.ask_download("test_file.txt")
        self.assertFalse(mock_asksaveasfilename.called)

    @patch("client.gui.messagebox.askyesno")
    @patch("client.gui.filedialog.asksaveasfilename")
    def test_ask_download_accept(self, mock_asksaveasfilename, mock_askyesno):
        """Test accepting a file download."""
        mock_askyesno.return_value = True
        mock_asksaveasfilename.return_value = "/path/to/save/test_file.txt"
        with patch("threading.Thread.start"):
            self.gui.ask_download("test_file.txt")
        mock_asksaveasfilename.assert_called_once()

if __name__ == "__main__":
    unittest.main()