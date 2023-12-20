import json
import socket
import sqlite3
import sys
import msvcrt
import errno
import bcrypt
import colorama
from colorama import *

colorama.init(autoreset=True)
HEADER_LENGTH = 10
# Set up the connection between the client and the server
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# Connecting the Database
connection = sqlite3.connect("AppData.db")
cursor = connection.cursor()


# The Register Function that checks that the username is Unique
def user_register(username, password):
    cursor.execute("SELECT * FROM AppData WHERE username=?", (username,))
    if cursor.fetchone() is None:
        username_header_register = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
        username_text = username.encode('utf-8')
        client_socket.send(username_header_register + username_text)
        Password_header_Register = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
        password_text = password.encode('utf-8')
        client_socket.send(Password_header_Register + password_text)
        client_socket.send('register'.encode('utf-8'))
        print("Welcome " + username + "")
        return True
    else:
        print(f'{Fore.RED} Username is not unique!')
        return False


# The login function that checks the username and the Password
def user_login(username, password):
    cursor.execute("SELECT password, salted_password FROM AppData WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hashed_password = result[0]
        stored_salt = result[1]
        entered_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)
        if entered_hashed_password == stored_hashed_password:
            username_header_login = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
            username_text = username.encode('utf-8')
            client_socket.send(username_header_login + username_text)
            Password_header_login = f'{len(password):<{HEADER_LENGTH}}'.encode('utf-8')
            password_text = password.encode('utf-8')
            client_socket.send(Password_header_login + password_text)
            client_socket.send('login'.encode('utf-8'))
            print("Welcome " + username + "")
            return True
        else:
            print(f'{Fore.RED} invalid username or password!')
            return False
    else:
        print(f'{Fore.RED}invalid username or password!')
        return False


# Choosing the Login Or Register For the Client
choice = input("1.login\n2.register\n")

if choice == '1':
    # This While Loop makes enter the username and Password again if the data is not correct
    LogingResult = False
    while not LogingResult:
        ClientUsername = input(f"{Fore.RESET}Enter Username: {Fore.LIGHTBLUE_EX}")
        ClientPassword = input(f"{Fore.RESET}Enter Password: {Fore.LIGHTBLUE_EX}")
        LogingResult = user_login(ClientUsername, ClientPassword)
else:
    RegisterResult = False
    while not RegisterResult:
        ClientUsername = input(f"{Fore.RESET}Enter Unique Username:{Fore.LIGHTBLUE_EX} ")
        ClientPassword = input(f"{Fore.RESET}Create Password: {Fore.LIGHTBLUE_EX}")
        RegisterResult = user_register(ClientUsername, ClientPassword)

while True:
    # Handling the sending of the Messages in JSON format
    if msvcrt.kbhit():
        message = input(f'{Fore.RESET}{ClientUsername} ->{Fore.LIGHTMAGENTA_EX} ')
        if message:
            json_message = json.dumps({'username': ClientUsername, 'message': message})
            message_header = f'{len(json_message):<{HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(message_header + json_message.encode('utf-8'))

    try:
        while True:
            message_header_received = client_socket.recv(HEADER_LENGTH)
            if not message_header_received:
                print('Connection closed by the server')
                sys.exit()

            message_length = int(message_header_received.decode('utf-8').strip())
            received_json_message = client_socket.recv(message_length).decode('utf-8')
            received_data = json.loads(received_json_message)
            print(f'{Fore.RESET}{received_data["username"]} -> {Fore.LIGHTBLUE_EX}{received_data["message"]}')

    # Handling Exceptions Like if the Server Closed
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print(f'{Fore.RED}Reading error:{str(e)} ')
            sys.exit()
        continue

    except Exception as e:
        print(f'{Fore.RED}Reading error:{str(e)} ')
        sys.exit()
