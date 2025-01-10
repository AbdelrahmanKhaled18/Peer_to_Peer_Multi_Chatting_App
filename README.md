# Peer-to-Peer Multi-Chatting App

The Peer-to-Peer Multi-Chatting App is a Python-based application leveraging socket programming to facilitate direct communication between users. Key features include:

* User Authentication: Secure login and registration.
* Online Users Listing: View active users.
* One-to-One Chat: Private messaging between users.
* Chat Rooms: Create, join, and participate in public or private chat rooms.
* Real-Time Communication: Messages are delivered instantly using peer-to-peer connections.

## Features

### User Authentication
- **Registration**: Users can create an account with a unique username and password.
- **Login**: Users can log in to their account using their credentials.

### Online Users Listing
- **View Active Users**: Users can see a list of currently online users.

### One-to-One Chat
- **Private Messaging**: Users can send private messages to other online users.

### Chat Rooms
- **Create Chat Rooms**: Users can create new chat rooms.
- **Join Chat Rooms**: Users can join existing chat rooms.
- **Participate in Chat Rooms**: Users can send and receive messages in chat rooms.

### Real-Time Communication
- **Instant Messaging**: Messages are delivered instantly using peer-to-peer connections.

## Installation

### Prerequisites
- Python 3.12
- MongoDB

### Libraries
- `sockets`: Used for client-server interaction.
- `threading`: Used for multithreading to enable multiple users to interact with the app simultaneously.
- `colorama`: Used for coloring the text in the command line interface.
- `bcrypt`: Used for password encryption for user authentication.

### Steps
1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the required libraries**:
    ```sh
    pip install colorama bcrypt
    ```

3. **Set up MongoDB**:
    - Ensure MongoDB is installed and running on your system.
    - Create a database and collection for storing user information.

4. **Run the Server**:
    ```sh
    python registry.py
    ```
5. **Run the Client**:
    ```sh
    python peer.py
    ```

## Usage

### Register a New Account
1. Run the application.
2. Select the option to create a new account.
3. Enter a unique username and password.

### Login to an Existing Account
1. Run the application.
2. Select the option to log in.
3. Enter your username and password.

### View Online Users
1. After logging in, select the option to view online users.

### Send a Private Message
1. After logging in, select the option to send a private message.
2. Enter the username of the user you want to message.
3. Type and send your message.

### Create a Chat Room
1. After logging in, select the option to create a chat room.
2. Enter a unique name for the chat room.

### Join a Chat Room
1. After logging in, select the option to join a chat room.
2. Enter the name of the chat room you want to join.

### Participate in a Chat Room
1. After joining a chat room, type and send messages to participate in the chat.

## Documentation

For detailed code documentation, please refer to the `P2P Multi_Chatting_Application.pdf` file included in the repository.

## Contributing

Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or inquiries, please contact [Your Name] at [your-email@example.com].