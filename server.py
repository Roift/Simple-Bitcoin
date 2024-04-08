from socket import *

# server configuration
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive.')

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

# process transaction
def processTransaction(transaction):
    payer = transaction['payer']
    amount = transaction['amount']
    payee1 = transaction['payee1']
    user = findUser(payer)

    # check if payer exists and has sufficient balance
    if not user or user['balance'] < amount:
        return f'TX {transaction["tx_id"]} rejected. Insufficient balance. Your current balance is {user["balance"]} BTC.'

    # deduct amount from payer's balance
    user['balance'] -= amount

    # add amount to payee1's balance
    payee = findUser(payee1)
    if payee:
        payee['balance'] += amount

    # store confirmed transaction
    transactions.append(transaction)

    return f'TX {transaction["tx_id"]} confirmed. Your current balance is {user["balance"]} BTC.'

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    message_parts = message.decode().split()

    # Check if the message is a valid request
    if len(message_parts) < 2:
        serverSocket.sendto('Invalid request format.'.encode(), clientAddress)
        continue

    command = message_parts[0].upper()

    if command == 'LOGIN':
        username = message_parts[1]
        password = message_parts[2]
        user = findUser(username)
        
        print('Authentication request received...')
        if not user or user['password'] != password: #if user or password doesn't match, send authentication failure message
            print ('Authentication failed!')
            serverSocket.sendto('Invalid username or password.'.encode(), clientAddress)
            continue

        # respond with user's balance and confirmed transactions on authentication success
        print ('Authentication success!')
        response = f'Login successful!\n Balance: {user["balance"]} BTC\n Transactions: {transactions}'
        serverSocket.sendto(response.encode(), clientAddress)

    elif command == 'VALIDATE':
        # Validate transaction amount
        username = message_parts[1]
        amount = float(message_parts[2])
        user = findUser(username)
        if not user or user['balance'] < amount:
            serverSocket.sendto('Transaction amount exceeds balance.'.encode(), clientAddress)
        else:
            serverSocket.sendto('Transaction amount is valid.'.encode(), clientAddress)

    elif command == 'TX':
        transaction = {}
        for part in message_parts[1:]:
            if '=' in part:
                key, value = part.split('=')
                transaction[key] = value

        if 'tx_id' not in transaction or 'amount' not in transaction or 'payer' not in transaction or 'payee1' not in transaction:
            serverSocket.sendto('Incomplete transaction details.'.encode(), clientAddress)
            continue

        tx_id = int(transaction['tx_id'])
        amount = float(transaction['amount'])
        payee1 = transaction['payee1']
        amount_to_payee1 = float(transaction['payment1']) if 'payment1' in transaction else None
        payee2 = transaction['payee2'] if 'payee2' in transaction else None
        amount_to_payee2 = float(transaction['payment2']) if 'payment2' in transaction else None

        if amount_to_payee1 is not None and (amount_to_payee1 < 0 or amount_to_payee1 > amount):
                serverSocket.sendto('Invalid payment amount for Payee1.'.encode(), clientAddress)
                continue
        if payee2 is not None and (amount_to_payee2 is None or amount_to_payee2 < 0 or amount_to_payee2 > (amount - amount_to_payee1)):
            serverSocket.sendto('Invalid payment amount for Payee2.'.encode(), clientAddress)
            continue

        # Create transaction dictionary
        transaction = {
            'tx_id': tx_id,
            'payer': transaction['payer'],
            'amount': amount,
            'payee1': payee1,
            'payment1': amount_to_payee1,
            'payee2': payee2,
            'payment2': amount_to_payee2
        }

        # Process transaction
        response = processTransaction(transaction)
        serverSocket.sendto(response.encode(), clientAddress)

    else:
        serverSocket.sendto('Invalid command.'.encode(), clientAddress)
