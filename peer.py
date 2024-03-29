from socket import *
import threading
import select
import logging
import colorama
from colorama import *

colorama.init(autoreset=True)


def formatting_print(msg):
    print("\u001B[s", end="")
    print("\u001B[A", end="")
    print("\u001B[999D", end="")
    print("\u001B[S", end="")
    print("\u001B[L", end="")
    print(msg, end="")
    print("\u001B[u", end="", flush=True)


# Server side of peer
class PeerServer(threading.Thread):

    # Peer server initialization
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.peerServerHostname = None

        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None  # da elly el client byd5lo w2t el login
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        # Available Chat Rooms
        self.current_chat_room = None
        # connected peers
        self.connectedPeers = []

    # main method of the peer server thread
    def run(self):

        print(f"{Fore.GREEN}{Style.BRIGHT}Peer server started...{Fore.RESET}")

        # gets the ip address of this peer
        # first checks to get it for Windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macOS devices
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        # self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
        # inputs sockets that should be listened to
        inputs = [self.tcpServerSocket]
        # the server listens as long as there is a socket to listen in the input list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs + self.connectedPeers, [], [], 1)
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is 
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket:
                        # accepts the connection, and adds its connection socket to the input list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        # inputs.append(connected)
                        self.connectedPeers.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # this peer are assigned to server variables
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
                    else:
                        try:
                            message = s.recv(1024).decode().split("\n")
                        except:
                            s.close()
                            self.connectedPeers.remove(s)
                            if self.current_chat_room is None:
                                self.isChatRequested = False
                            continue

                        if len(message) == 0:
                            s.close()
                            self.connectedPeers.remove(s)
                        elif message[0] == "one-to-one-chat-request":
                            if self.isChatRequested:
                                if self.current_chat_room:
                                    s.send(f"user-chatting\n{self.current_chat_room}".encode())
                                else:
                                    s.send(f"user-chatting".encode())
                            else:
                                self.isChatRequested = 1
                                formatting_print(f"Receiving chat request from {message[1]}")
                                formatting_print("Would you like to accept (YES/NO)")

                        elif message[0] == "chatroom-join":
                            if message[1] == self.current_chat_room:
                                formatting_print(f"{message[2]} has joined the chatroom.")
                                s.send("welcome".encode())
                            else:
                                s.send("user-not-in-chatroom".encode())

                        elif message[0] == "chatroom-leave":
                            formatting_print(
                                f"{Fore.RED}{message[1]} " + f"{Fore.RED}has left the chatroom.{Fore.RESET}")
                            s.close()
                            self.connectedPeers.remove(s)
                        elif message[0] == "chat-message":
                            username = message[1]
                            content = "\n".join(message[2:])
                            formatting_print(username + " -> " + f"{Fore.LIGHTBLUE_EX}{content}{Fore.RESET}")

                        elif message[0] == "one-to-one-chat-end":
                            formatting_print(f"{message[1]} has ended the chat.")
                            self.isChatRequested = 0
                            s.close()
                            self.connectedPeers.remove(s)

            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))


# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self, peerServer, peersToConnect=None, chatRoom=None):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        self.peerServer = peerServer

        # keeps the username of the peer
        self.peerServer.current_chat_room = chatRoom

        self.peerServer.isChatRequested = 1
        # keeps the port number that this client should connect

        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client

        # keeps the phrase used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        # self.responseReceived = responseReceived
        # keeps if this client is ending the chat or not
        self.isEndingChat = False

        if peersToConnect is not None:
            for peer in peersToConnect:
                peer_data = peer.split(":")
                if len(peer_data) >= 2:
                    peerHost = peer_data[0]
                    peerPort = int(peer_data[1])
                    sock = socket(AF_INET, SOCK_STREAM)
                    sock.connect((peerHost, peerPort))
                    if chatRoom is not None:
                        sock.send(f"chatroom-join\n{chatRoom}\n{self.peerServer.username}".encode())
                        response = sock.recv(1024).decode()
                        if response == "welcome":
                            self.peerServer.connectedPeers.append(sock)

                    else:
                        sock.send(f"one-to-one-chat-request\n{self.peerServer.username}".encode())
                        response = sock.recv(1024).decode().split("\n")

                        if response[0] == "user-chatting":
                            self.peerServer.isChatRequested = 0
                            if len(response) == 1:
                                print("User is already in a private chat")
                            else:
                                print(f"User is in chatroom: {response[1]}")

                        elif response[0] == "chat-request-reject":
                            print("User has rejected the chat request")
                            self.peerServer.isChatRequested = 0

                        elif response[0] == "chat-request-accept":
                            self.peerServer.connectedPeers.append(sock)
                            print("User has accepted the chat.")

    # main method of the peer client thread
    def run(self):
        if self.peerServer.isChatRequested:
            if self.peerServer.current_chat_room:
                print(f"{Fore.RED}Chatroom joined Successfully.{Fore.RESET}")
            print(f"{Fore.RED}Start typing to send a message. Send ':exit' to leave the chatroom.{Fore.RESET}")

        while self.peerServer.isChatRequested:
            content = input("-> ")

            if content == ":exit":
                if self.peerServer.current_chat_room is None:
                    message = f"one-to-one-chat-end\n{self.peerServer.username}"
                else:
                    message = f"chatroom-leave\n{self.peerServer.username}"
            else:
                message = f"chat-message\n{self.peerServer.username}\n{content}"

            for sock in self.peerServer.connectedPeers:
                sock.send(message.encode())

            if content == ":exit":
                self.peerServer.isChatRequested = 0
                self.peerServer.current_chat_room = None
                for sock in self.peerServer.connectedPeers:
                    sock.close()
                self.peerServer.connectedPeers = []


# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self, username=None):
        # ip address of the registry
        self.registryName = input(f"{Fore.RED}Enter IP address of registry: {Fore.LIGHTBLUE_EX}")
        # self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = 15400
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName, self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15300
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None
        # available chat rooms
        self.chat_rooms = []
        self.username = username

        choice = "0"
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        while choice != "3":
            if not self.isOnline:
                # menu selection prompt
                choice = input(f"{Fore.RESET}Choose: \nCreate account: 1\nLogin: 2\n")

                # if choice is 1, creates an account with the username
                # and password entered by the user
                if choice == "1":
                    username = input(f"username: {Fore.LIGHTBLUE_EX}")
                    password = input(f"{Fore.RESET}password: {Fore.LIGHTBLUE_EX}")

                    self.createAccount(username, password)
                # if choice is 2 and user is not logged in, asks for the username
                # and the password to login
                elif choice == "2" and not self.isOnline:
                    username = input(f"{Fore.RESET}username: {Fore.LIGHTBLUE_EX}")
                    password = input(f"{Fore.RESET}password: {Fore.LIGHTBLUE_EX}")
                    # asks for the port number for server's tcp socket
                    peerServerPort = int(input(f"{Fore.RESET}Enter a port number for peer server: "))

                    status = self.login(username, password, peerServerPort)
                    # is user logs in successfully, peer variables are set
                    if status == 1:
                        self.isOnline = True
                        self.loginCredentials = (username, password)
                        self.username = username
                        self.peerServerPort = peerServerPort
                        # creates the server thread for this peer, and runs it
                        self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort)
                        self.peerServer.start()
                        # hello message is sent to registry
                        self.sendHelloMessage()
                # if choice is 3 and user is logged in, then user is logged out
                # and peer variables are set, and server and client sockets are closed
            elif self.isOnline:

                choice = input(f"{Fore.RESET}Choose: \nLogout: 3\nSearch: "
                               f"4\nStart a Chat: 5\nCreate Chat Room: 6\nJoin Chat: 7\n"
                               f"List Users: 8\nList Chat Rooms: 9\n")
                if choice == "3" and self.isOnline:
                    self.logout(1)
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcpServerSocket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcpClientSocket.close()
                    print("Logged out successfully")
                # is peer not logged in and exits the program?
                elif choice == "3":
                    self.logout(2)
                # if choice is 4 and user is online, then user is asked
                # for a username wanted to be searched
                elif choice == "4" and self.isOnline:
                    username = input("Username to be searched: ")
                    searchStatus = self.searchUser(username)
                    # if user is found its ip address is shown to the user
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        print(f"{Fore.RED}IP address of " + username + " is " +
                              searchStatus[0] + " and the Port number is " + searchStatus[1] + f"{Fore.RESET}")

                # if choice is 5 and user is online, then user is asked
                # to enter the username of the user that is wanted to be chatted
                elif choice == "5" and self.isOnline:
                    username = input("Enter the username of user to start chat: ")
                    searchStatus = self.searchUser(username)
                    # if searched user is found, then its ip address and port number is retrieved,
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(self.peerServer, [f"{searchStatus[0]}:{searchStatus[1]}"])
                        self.peerClient.start()
                        self.peerClient.join()
                        self.peerClient = None

                # Creating chat room
                elif choice == "6":
                    chat_name = input(f"Enter the Chat room name to Create: {Fore.RED}")
                    self.Create_Chat_Room(chat_name)
                # Joining Chat room
                elif choice == "7":
                    chat_name = input(f"Enter the Chat room name to Join: {Fore.RED}")
                    self.Join_Chat_Room(chat_name)
                # listing online users
                elif choice == "8":
                    self.userList()
                # listing chat rooms
                elif choice == "9":
                    self.roomsList()

                elif choice == "YES" and self.isOnline:
                    if self.peerServer.isChatRequested:
                        sock = self.peerServer.connectedPeers[0]
                        sock.send("chat-request-accept".encode())
                        self.peerClient = PeerClient(self.peerServer)
                        self.peerClient.start()
                        self.peerClient.join()
                    else:
                        print("Invalid input. Please try again")
                # if user rejects the chat request then reject a message is sent to the requester side
                elif choice == "NO" and self.isOnline:
                    if self.peerServer.isChatRequested:
                        sock = self.peerServer.connectedPeers[0]
                        sock.send("chat-request-reject".encode())
                        self.peerServer.isChatRequested = 0
                    else:
                        print("Invalid input. Please try again")
            # if choice is cancel timer for hello message is canceled
            # elif choice == "CANCEL":
            #     self.timer.cancel()
            #     break
        # if the main process is not ended with cancel selection
        # socket of the client is closed
        # if choice != "CANCEL":
        #     self.tcpClientSocket.close()

    # account creation function
    def createAccount(self, username, password):
        # join a message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response exists then informs the user for account existence
        message = "JOIN " + username + " " + password
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response == "join-success":
            print("Account created...")
        elif response == "join-exist":
            print("choose another username or login...")

    def Create_Chat_Room(self, chat_room_name):
        message = "CREATE " + chat_room_name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response.startswith("create-success"):
            creator = response[len("create-success "):]  # Extract the creator's username
            print(f"{Fore.GREEN}Chat room {chat_room_name} was created successfully by {creator}{Fore.RESET}")
            self.Join_Chat_Room(chat_room_name)
            # self.peerClient = PeerClient(self.username, self.peerServer, chat_room_name)
            # self.peerClient.start()
            # self.peerClient.join()
        else:
            print(f"{Fore.RED}There is already a chat room with that name.{Fore.RESET}")

    def userList(self):
        message = "users-list-request" + " "
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response.startswith("users-list"):
            users = response[len("users-list"):].split('\n')
            print("Online Users:\n")
            if len(users) > 1:  # Check if there are users listed
                for user in users[1:]:
                    print(f"{Fore.RED}{user}" + ",")
                print(f"{Fore.RESET}\n")
            else:
                print("\tNo users currently online")
        else:
            print("Unexpected response:", response)

    def roomsList(self):
        message = "rooms-list-request"
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response.startswith("chat-list"):
            chats = response[len("chat-list\n"):].split(',')
            print("Available Rooms:")
            for chat in chats:
                chat_name = chat.strip()
                if chat_name:  # Ensure the room name is not an empty string
                    print(f"{Fore.RED}{chat_name}{Fore.RESET}")
            print("\n")
            if len(chats) < 1:  # Check if only the header or no rooms exist
                print("\tNo rooms currently exist")
        else:
            print("Unexpected response:", response)

    def Join_Chat_Room(self, chat_room_name):
        message = "JOIN-CHAT " + chat_room_name + " "
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response.startswith("join-chat-success"):
            participants_list = response.split()[1:]  # Extract the list of participants
            if participants_list:
                print("Joined " + chat_room_name + "\n. Participants: " + ", ".join(participants_list))
                self.peerClient = PeerClient(self.peerServer, participants_list, chat_room_name)
                self.peerClient.start()
                self.peerClient.join()
            else:
                # If participants_list is empty, initiate the PeerClient without the list
                print("Joined " + chat_room_name + ". No participants in the room yet.")
                self.peerClient = PeerClient(self.peerServer, None, chat_room_name)
                self.peerClient.start()
                self.peerClient.join()

            self.tcpClientSocket.send("chatroom-leave".encode())
            self.peerClient = None
        elif response == "No-Room found":
            print("No room found by the name: " + chat_room_name)

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # and integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        if response == "login-success":
            print("Logged in successfully...")
            return 1
        elif response == "login-account-not-exist":
            print("Account does not exist...")
            return 0
        elif response == "login-online":
            print("Account is already online...")
            return 2
        elif response == "login-wrong-password":
            print("Wrong password...")
            return 3

    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        self.tcpClientSocket.send(message.encode())

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "search-success":
            print(f"{Fore.LIGHTGREEN_EX}" + username + f" is found successfully...{Fore.RESET}")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()


# peer is started
main = peerMain()
