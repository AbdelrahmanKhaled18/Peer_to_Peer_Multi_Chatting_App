import json
import socket
import sqlite3
import threading
import colorama
import bcrypt
from colorama import *

HEADER_LENGTH = 10
Flag = True
colorama.init(autoreset=True)

# Set up the Connection for the Server Using Sockets
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]
clients = {}
print(f'{Fore.RED}Listening for connection on {IP}:{PORT}{Fore.RESET}')


# Function Used to Receives Msgs From the Client
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        return False


# Function To Add the user in the Database in  case of Register
def add_user(username, password):
    # Connecting the Database File
    connection = sqlite3.connect("AppData.db")
    cursor = connection.cursor()

    # Generating Salt For The salted Hashing using bcrypt
    salt = bcrypt.gensalt()
    cursor.execute("INSERT INTO AppData(username, password,salted_password) VALUES (?, ? ,?)",
                   (username, bcrypt.hashpw(password.encode("utf-8"), salt), salt))
    connection.commit()
    connection.close()


# Functions used to handle single Client
def handle_client(client_socket, address):
    global Flag
    user = receive_message(client_socket)
    if user is False:
        return
    clients[client_socket] = user
    Flag = False
    print(f'{Fore.RESET}Accepted connection from {Fore.LIGHTBLUE_EX}{address} {Fore.RESET}username: '
          f'{Fore.LIGHTBLUE_EX}{user["data"].decode("utf-8")}')

    # Accepting messages algorithm
    while True:
        if client_socket in clients and not Flag:
            password = receive_message(client_socket)
            user_object = clients[client_socket]
            result = client_socket.recv(1024).decode('utf-8')
            if result == 'register':
                add_user(user_object['data'].decode('utf-8'), password['data'].decode('utf-8'))
                print('Registered for user:{0}'.format(user_object['data'].decode('utf-8')))
            Flag = True
        else:
            message = receive_message(client_socket)
            # if no message then the connection is closed between this client  and the server
            if message is False:
                print(f'{Fore.RED}Connection closed from: '
                      f'{clients[client_socket]["data"].decode("utf-8")} {Fore.RESET}')
                try:
                    socket_list.remove(client_socket)
                except ValueError:
                    pass
                del clients[client_socket]
                break

            user_object = clients[client_socket]
            sender_username = user_object['data'].decode('utf-8')
            # Exchanging the messages in a JSON format
            received_json = message['data'].decode('utf-8')
            received_data = json.loads(received_json)
            received_username = received_data['username']
            received_message = received_data['message']

            print(f"{Fore.RESET}Received message from {received_username}: {Fore.RED}{received_message} {Fore.RESET}")

            json_message = json.dumps({'username': sender_username, 'message': received_message})

            for client_sock in clients:
                if client_sock != client_socket:
                    client_sock.send(
                        f'{len(json_message):<{HEADER_LENGTH}}'.encode('utf-8') + json_message.encode('utf-8')
                    )

    client_socket.close()


# Handling the Multithreading in The file to make every client on a Separate thread
while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()
