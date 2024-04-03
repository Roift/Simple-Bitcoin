from socket import *

# server configuration
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')

# define list to store user information
users = [
    {'username': 'A', 'password': 'A', 'balance': 10},
    {'username': 'B', 'password': 'B', 'balance': 10},
    {'username': 'C', 'password': 'C', 'balance': 10},
    {'username': 'D', 'password': 'D', 'balance': 10}
]

# define a list to store confirmed transactions
transactions = []

# search for user
def findUser(username):
    for user in users:
        if user['username'] == username:
            return user
    return None

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    message_parts = message.decode().split()

    # Check if the message is a valid request
    if len(message_parts) < 3:
        serverSocket.sendto('Invalid request format.'.encode(), clientAddress)
        continue

    command = message_parts[0].upper()
    username = message_parts[1]
    password = message_parts[2]
    user = findUser(username)

    if command == 'LOGIN':
        if not user or user['password'] != password: #if user or password doesn't match, send authentication failure message
            serverSocket.sendto('Invalid username or password.'.encode(), clientAddress)
            continue

        # respond with user's balance and confirmed transactions on authentication success
        response = f'Login successful!\n Balance: {user["balance"]} BTC\n Transactions: {transactions}'
        serverSocket.sendto(response.encode(), clientAddress)