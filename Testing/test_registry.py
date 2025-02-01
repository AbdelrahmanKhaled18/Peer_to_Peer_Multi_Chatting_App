import sys
import unittest
from unittest.mock import MagicMock, patch, Mock
from io import StringIO
import socket
import threading
import time

import client
# Import the functions and classes you want to test
from server import *


class TestClientThread(unittest.TestCase):
    def setUp(self):
        self.mock_socket = Mock()
        self.peer_instance = client.peerMain()
        self.peer_instance.tcpClientSocket = MagicMock()
        self.peer_instance.registryName = 'testRegistry'
        self.peer_instance.registryPort = 15400

    def tearDown(self):
        self.peer_instance.tcpClientSocket.close()

    @patch('threading.Timer')
    def test_send_hello_message(self, mock_timer):
        # Arrange
        self.peer_instance.loginCredentials = ('testUser', 'testPassword')
        self.peer_instance.udpClientSocket.sendto.return_value = None
        mock_timer_instance = mock_timer.return_value
        mock_timer_instance.start.return_value = None

        # Act
        self.peer_instance.sendHelloMessage()

        # Assert
        self.peer_instance.udpClientSocket.sendto.assert_called_once()
        mock_timer.assert_called_once_with(1, self.peer_instance.sendHelloMessage)
        mock_timer_instance.start.assert_called_once()

    def test_create_account_success(self):
        # Arrange
        username = 'testUser'
        password = 'testPassword'
        self.peer_instance.tcpClientSocket.recv.return_value = b'join-success'
        sys.stdout = StringIO()

        # Act
        self.peer_instance.createAccount(username, password)

        # Assert
        self.peer_instance.tcpClientSocket.send.assert_called_once_with(b'JOIN testUser testPassword')
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, Fore.LIGHTGREEN_EX + "Account created...")




    # def test_login_account_not_exist(self):
    #     # Mocking the database to return False for account existence
    #     with unittest.mock.patch('registry.db.is_account_exist', return_value=False):
    #         client_thread = ClientThread('127.0.0.1', 1234, self.mock_socket)
    #         # Replace message[1], message[2], message[3] with appropriate values
    #         client_thread.message = ["", "username_not_existing", "password", "port_number"]
    #         client_thread.login()
    #         self.mock_socket.send.assert_called_with("login-account-not-exist".encode())

    # def test_signup(self):
    #     # Test JOIN with a nonexistent account
    #     client_thread = ClientThread('127.0.0.1', 1234, self.mock_socket)
    #     self.assertTrue(client_thread.join_account('new_user', 'password'))

    # Add more test cases for other functions in ClientThread


class TestUDPServer(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or data for testing
        self.mock_tcp_socket = MagicMock()
        self.mock_tcp_socket.send.return_value = None

    def test_wait_hello_message(self):
        # Test waitHelloMessage method
        udp_server = UDPServer('test_user', self.mock_tcp_socket)
        udp_server.waitHelloMessage()  # This should not raise an exception

    # Add more test cases for other functions in UDPServer


if __name__ == '__main__':
    unittest.main()
