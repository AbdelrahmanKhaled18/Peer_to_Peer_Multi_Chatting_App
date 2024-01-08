from socket import *
import threading
import select
import logging
import db
import bcrypt
import colorama
from colorama import *

colorama.init(autoreset=True)


# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created

def is_account_online(username):
    for peer in onlinePeers:
        if peer["username"] == username:
            return True
    return False


def get_peer_ip_port(username):
    for peer in onlinePeers:
        if peer["username"] == username:
            return (peer["ip"], peer["port"])
    return (None, None)


class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.chatroom = None
        self.lock = None
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        print("New thread started for " + ip + ":" + str(port))

    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(port))
        print("IP Connected: " + self.ip)

        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split()
                #   JOIN #
                if message[0] == "JOIN":
                    self.create_account(message[1], message[2])
                #   LOGIN    #
                elif message[0] == "LOGIN":
                    self.login(message[1], message[2], message[3])

                #   LOGOUT  #
                elif message[0] == "LOGOUT":
                    # if a user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed, and the timer thread of the udp for this
                    # user is canceled
                    if self.chatroom is not None:
                        self.leave_chat_room()

                    if len(message) > 1 and message[1] is not None and is_account_online(message[1]):
                        for peer in onlinePeers:
                            if peer["username"] == message[1]:
                                onlinePeers.remove(peer)
                                break
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #   SEARCH #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if is_account_online(message[1]):
                            peer_info_ip, peer_info_port = get_peer_ip_port(message[1])
                            if peer_info_ip and peer_info_port:
                                response = f"search-success {peer_info_ip}:{peer_info_port}"

                                self.tcpClientSocket.send(response.encode())
                            else:
                                response = "search-user-not-found"  # Unable to fetch IP and port for the username

                                self.tcpClientSocket.send(response.encode())
                        else:
                            response = "search-user-not-online"

                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist 
                    else:
                        response = "search-user-not-found"

                        self.tcpClientSocket.send(response.encode())

                # CREATE CHAT ROOM
                elif message[0] == "CREATE":
                    room_name = message[1]  # Extract room name from the message
                    room_exists = any(room['name'] == room_name for room in chat_rooms)
                    if room_exists:
                        response = "create-failed" + " "  # Room already exists
                    else:
                        response = "create-success " + self.username  # Room creation successful
                        chat_rooms.append({"name": room_name, "participants": []})
                    self.tcpClientSocket.send(response.encode())

                # JOIN CHAT ROOM
                elif message[0] == "JOIN-CHAT":
                    requested_room_name = message[1]
                    room_exists = False
                    ip_1, port_1 = get_peer_ip_port(self.username)
                    for room in chat_rooms:
                        if room["name"] == requested_room_name:
                            participants_list = [f"{participant['ip']}:{participant['port']}"
                                                 for participant in room["participants"]]

                            room["participants"].append({"username": self.username, "ip": ip_1, "port": port_1})
                            self.chatroom = requested_room_name
                            # Collect all participants' IP and port in the room

                            response = "join-chat-success " + " ".join(participants_list)
                            self.tcpClientSocket.send(response.encode())
                            room_exists = True
                            break
                    if not room_exists:
                        response = "No-Room found"
                        self.tcpClientSocket.send(response.encode())

                # ONLINE USERS LIST
                elif message[0] == "users-list-request":
                    if onlinePeers:
                        users = ",".join([peer["username"] for peer in onlinePeers])
                        response = f"users-list\n{users}"
                        self.tcpClientSocket.send(response.encode())
                    else:
                        # If no users are online, send a message indicating that
                        response = "users-list\nNo users online"
                        self.tcpClientSocket.send(response.encode())

                # CHAT ROOMS LIST
                elif message[0] == "rooms-list-request":
                    if chat_rooms:
                        # Filter out non-string room names and join them
                        chats = ",".join([room["name"] for room in chat_rooms if isinstance(room["name"], str)])
                        response = f"chat-list\n{chats}"
                        self.tcpClientSocket.send(response.encode())
                    else:
                        # If no rooms are available, send a message indicating that
                        response = "chat-list\nNo rooms available"
                        self.tcpClientSocket.send(response.encode())

                # LEAVING the CHAT ROOM
                elif message[0] == "chatroom-leave":
                    self.leave_chat_room()
            except OSError as oErr:
                pass

    # function for resetting the timeout for the udp timer thread
    def resetTimeout(self):
        self.udpServer.resetTimer()

    def login(self, username, password, port_login):
        # login-account-not-exist is sent to peer
        # if an account with the username does not exist
        if not db.is_account_exist(username):
            response = "login-account-not-exist"

            self.tcpClientSocket.send(response.encode())
        # login-online is sent to peer
        # if an account with the username already online
        elif is_account_online(username):
            response = "login-online"
            self.tcpClientSocket.send(response.encode())
            # onlinePeers.append(message[1])
        # login-success is sent to peer
        # if an account with the username exists and not online
        else:
            # retrieves the account's password, and checks if the one entered by the user is correct
            retrievedPass = db.get_password(username)
            # if the password is correct, then peer's thread is added to thread list
            # peer is added to db with its username, port number, and ip address
            if bcrypt.checkpw(password.encode('utf-8'), retrievedPass):
                self.username = username
                self.lock.acquire()
                try:
                    tcpThreads[self.username] = self
                finally:
                    self.lock.release()

                # login-success is sent to peer,
                # and an udp server thread is created for this peer, and thread is started
                # timer thread of the udp server is started
                response = "login-success"
                onlinePeers.append({"username": self.username, "ip": self.ip, "port": port_login})

                self.tcpClientSocket.send(response.encode())
                self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                self.udpServer.start()
                self.udpServer.timer.start()
            # if password not matches and then login-wrong-password response is sent
            else:
                response = "login-wrong-password"
                self.tcpClientSocket.send(response.encode())

    def create_account(self, username, password):
        # join-exist is sent to peer,
        # if an account with this username already exists
        if db.is_account_exist(username):
            response = "join-exist"
            print("From-> " + self.ip + ":" + str(self.port) + " " + response)

            self.tcpClientSocket.send(response.encode())
        # join-success is sent to peer,
        # if an account with this username does not exist, and the account is created
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db.register(username, hashed_password)
            response = "join-success"
            self.tcpClientSocket.send(response.encode())

    def leave_chat_room(self):
        for room in chat_rooms:
            for participant in room['participants']:
                if participant['username'] == self.username:
                    room['participants'].remove(participant)
                    self.chatroom = None
                    print(f"{self.username} left the chat room")
                    break


# implementation of the udp server thread for clients
class UDPServer(threading.Thread):

    # udp server thread initializations
    def __init__(self, username, clientSocket):
        threading.Thread.__init__(self)
        self.username = username
        # timer thread for the udp server is initialized
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.tcpClientSocket = clientSocket

    # if hello message is not received before timeout
    # then peer is disconnected
    def waitHelloMessage(self):
        for peer in onlinePeers:
            if peer["username"] is not None:
                onlinePeers.remove(peer)
                if self.username in tcpThreads:
                    del tcpThreads[self.username]
                    break
        self.tcpClientSocket.close()
        print("Removed " + self.username + " from online peers")

    # resets the timer for udp server
    def resetTimer(self):
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.timer.start()


# tcp and udp server port initializations
print(f"{Fore.RED}Registry started...{Fore.RESET}")
port = 15400
portUDP = 15300

# db initialization
db = db.DB()

# gets the ip address of this peer
# first checks to get it for Windows devices
# if the device that runs this application is not windows
# it checks to get it for macOS devices
hostname = gethostname()
try:
    host = gethostbyname(hostname)
except gaierror:
    import netifaces as ni

    host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

print(f"{Fore.RED}Registry IP address: {Fore.RESET}" + f"{Fore.LIGHTBLUE_EX} {host}{Fore.RESET}")
print(f"{Fore.RED}Registry port number: {Fore.RESET}" + f"{Fore.LIGHTBLUE_EX}{str(port)}{Fore.RESET}")

# onlinePeers list for an online account
onlinePeers = []
# chat rooms
chat_rooms = []
# accounts list for accounts
accounts = {}
# tcpThreads list for online client's thread
tcpThreads = {}

# tcp and udp socket initializations
tcpSocket = socket(AF_INET, SOCK_STREAM)
udpSocket = socket(AF_INET, SOCK_DGRAM)
tcpSocket.bind((host, port))
udpSocket.bind((host, portUDP))
tcpSocket.listen(5)

# input sockets that are listened to
inputs = [tcpSocket, udpSocket]

# log file initialization


# as long as at least a socket exists to listen registry runs
while inputs:

    print(f"{Fore.LIGHTGREEN_EX}Listening for incoming connections... {Fore.RESET}")
    # monitors for the incoming connections
    readable, writable, exceptional = select.select(inputs, [], [])
    for s in readable:
        # if the message received comes to the tcp socket
        # the connection is accepted and a thread is created for it, and that thread is started
        if s is tcpSocket:
            tcpClientSocket, addr = tcpSocket.accept()
            newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
            newThread.start()
        # if the message received comes to the udp socket
        elif s is udpSocket:
            # received the incoming udp message and parses it
            message, clientAddress = s.recvfrom(1024)
            message = message.decode().split()
            # checks if it is a hello message
            if message[0] == "HELLO":
                # checks if the account that this hello message 
                # is sent from is online
                if message[1] in tcpThreads:
                    # resets the timeout for that peer since the hello message is received
                    tcpThreads[message[1]].resetTimeout()
                    print("Hello is received from " + message[1])

# registry tcp socket is closed
tcpSocket.close()
