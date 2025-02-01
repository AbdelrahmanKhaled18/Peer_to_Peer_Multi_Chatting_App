import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from contextlib import redirect_stdout
from colorama import Fore
from client import peerMain

class TestPeerMain(unittest.TestCase):
    def setUp(self):
        # Initialize any resources needed for tests
        pass

    def tearDown(self):
        # Clean up any resources created during tests
        pass

    @patch('builtins.input', side_effect=["192.168.1.106","1", "testuser", "testpassword"])
    def test_create_account(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main = peerMain()
            main.createAccount("testuser", "testpassword")
            output = mock_stdout.getvalue().strip()
            self.assertEqual(output, "Account created...")

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_login_success(self, mock_stdout, mock_input):
        with self.assertRaises(SystemExit):
            main = peerMain()
        output = mock_stdout.getvalue()
        self.assertIn("Logged in successfully", output)

    @patch('builtins.input', side_effect=['3'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_logout(self, mock_stdout, mock_input):
        with self.assertRaises(SystemExit):
            main = peerMain()
        output = mock_stdout.getvalue()
        self.assertIn("Logged out successfully", output)

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234','4', 'test_search_user'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_search_user_online(self, mock_stdout, mock_input):
        with self.assertRaises(SystemExit):
            main = peerMain()
        output = mock_stdout.getvalue()
        self.assertIn("test_search_user is found successfully", output)

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234','5', 'test_user_to_chat'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_start_chat(self, mock_stdout, mock_input):
        with self.assertRaises(SystemExit):
            main = peerMain()
        output = mock_stdout.getvalue()
        self.assertIn("Peer client started", output)

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234',"6", "testchatroom"])
    def test_create_chat_room(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main = peerMain()
            main.Create_Chat_Room("testchatroom")
            output = mock_stdout.getvalue().strip()
            expected_output = f"{Fore.GREEN}Chat room testchatroom was created successfully by None{Fore.RESET}"
            self.assertEqual(output, expected_output)

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234',"7", "testchatroom"])
    def test_join_chat_room(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main = peerMain()
            main.Join_Chat_Room("testchatroom")
            output = mock_stdout.getvalue().strip()
            expected_output = "No room found by the name: testchatroom"
            self.assertEqual(output, expected_output)

    @patch('builtins.input', side_effect=["192.168.1.106",'2', 'test_user', 'test_password', '1234',"8"])
    def test_user_list(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main = peerMain()
            main.userList()
            output = mock_stdout.getvalue().strip()
            self.assertIn("No users currently online", output)

    @patch('builtins.input', side_effect=["9"])
    def test_rooms_list(self, mock_input):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main = peerMain()
            main.roomsList()
            output = mock_stdout.getvalue().strip()
            self.assertIn("No rooms currently exist", output)

    # Add more test methods for other functions...

if __name__ == "__main__":
    unittest.main()
