from socket import *

# Server configuration
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive.')

# Define list to store user information
users = [
    {'username': 'A', 'password': 'A', 'balance': 10},
    {'username': 'B', 'password': 'B', 'balance': 10},
    {'username': 'C', 'password': 'C', 'balance': 10},
    {'username': 'D', 'password': 'D', 'balance': 10}
]

# Define a list to store confirmed transactions
transactions = []

# Search for user
def findUser(username):
    for user in users:
        if user['username'] == username:
            return user
    return None

# Process transaction
def processTransaction(transaction):
    payer = transaction['payer']
    amount = transaction['amount']
    payee1 = transaction['payee1']
    user = findUser(payer)

    if not user or user['balance'] < amount:
        print(f'Received a transaction request from {payer}. Insufficient balance. Transaction rejected.')
        return f'TX {transaction["tx_id"]} rejected. Insufficient balance. Your current balance is {user["balance"]} BTC.'

    user['balance'] -= amount

    payee = findUser(payee1)
    if payee:
        payee['balance'] += amount

    transactions.append(transaction)

    print(f'Transaction {transaction["tx_id"]} confirmed. Balance updated for {payer} and {payee1}.')
    transaction['status'] = 'confirmed'
    return f'TX {transaction["tx_id"]} confirmed. Your current balance is {int(user["balance"])} BTC.'

def process_temporary_transaction(transaction):
    payer = transaction['payer']
    amount = transaction['amount']
    user = findUser(payer)

    if not user or user['balance'] < amount:
        print(f'Received a temporary transaction request from {payer}. Insufficient balance. Transaction rejected.')
        return f'TX {transaction["tx_id"]} rejected. Insufficient balance. Your current balance is {int(user["balance"])} BTC.'

    user['balance'] -= amount

    transactions.append(transaction)

    print(f'Temporary transaction {transaction["tx_id"]} received and processed.')
    transaction['status'] = 'temporary'
    return f'TX {transaction["tx_id"]} temporary transaction received.'


def get_user_transactions(username):
    user_transactions = []
    for transaction in transactions:
        if transaction['payer'] == username or transaction['payee1'] == username or transaction.get('payee2') == username:
            user_transactions.append(transaction)
    return user_transactions

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    message_parts = message.decode().split()

    if len(message_parts) < 2:
        serverSocket.sendto('Invalid request format.'.encode(), clientAddress)
        continue

    command = message_parts[0].upper()

    if command == 'LOGIN':
        username = message_parts[1]
        password = message_parts[2]
        user = findUser(username)
        
        if not user or user['password'] != password:
            print(f'Authentication request received from {username}. Authentication failed.')
            serverSocket.sendto('Invalid username or password.'.encode(), clientAddress)
            continue

        response = f'Login successful!\nBalance: {int(user["balance"])}'
        print(f'{username} is authenticated.')
        serverSocket.sendto(response.encode(), clientAddress)

    elif command == 'VALIDATE':
        username = message_parts[1]
        amount = float(message_parts[2])
        user = findUser(username)
        if not user or user['balance'] < amount:
            print(f'Validation request received from {username}. Transaction amount exceeds balance. Validation failed.')
            serverSocket.sendto('Transaction amount exceeds balance.'.encode(), clientAddress)
        else:
            print(f'Validation request received from {username}. Transaction amount is valid.')
            serverSocket.sendto('Transaction amount is valid.'.encode(), clientAddress)

    elif command == 'TX':
        transaction = {}
        for part in message_parts[1:]:
            if '=' in part:
                key, value = part.split('=')
                transaction[key] = value

        if 'tx_id' not in transaction:
            serverSocket.sendto('Transaction ID is missing.'.encode(), clientAddress)
            continue

        try:
            tx_id = int(transaction['tx_id'])
        except ValueError:
            serverSocket.sendto('Invalid transaction ID.'.encode(), clientAddress)
            continue

        amount = float(transaction['amount'])
        payer = transaction['payer']
        payee1 = transaction['payee1']
        amount_to_payee1 = float(transaction['payment1']) if 'payment1' in transaction else None
        payee2 = transaction['payee2'] if 'payee2' in transaction else None
        amount_to_payee2 = float(transaction['payment2']) if 'payment2' in transaction else None
        status = transaction['status'] if 'status' in transaction else 'temporary'  # Set status here if not received from client

        if amount_to_payee1 is not None and (amount_to_payee1 < 0 or amount_to_payee1 > amount):
            serverSocket.sendto('Invalid payment amount for Payee1.'.encode(), clientAddress)
            continue
        if payee2 is not None and (amount_to_payee2 is None or amount_to_payee2 < 0 or amount_to_payee2 > (amount - amount_to_payee1)):
            serverSocket.sendto('Invalid payment amount for Payee2.'.encode(), clientAddress)
            continue

        transaction = {
            'tx_id': tx_id,
            'payer': payer,
            'amount': amount,
            'payee1': payee1,
            'payment1': amount_to_payee1,
            'payee2': payee2,
            'payment2': amount_to_payee2,
            'status': status  # Ensure status is set properly
        }

        # Check if the transaction is temporary
        if status == 'temporary':
            response = process_temporary_transaction(transaction)
        else:
            response = processTransaction(transaction)

        serverSocket.sendto(response.encode(), clientAddress)


    elif command == 'TX_LIST':
        username = message_parts[1]
        user_transactions = get_user_transactions(username)
        response = "TX ID  | Payer | Amount | Payee1 | Amount | Payee2 | Amount | Status\n"
        response += "-" * 71 + "\n"  # Adding a line to separate header and data
        for tx in user_transactions:
            tx_id = str(tx['tx_id']).ljust(6)
            payer = tx['payer'].ljust(6)
            amount = str(tx['amount']).ljust(7)
            payee1 = tx['payee1'].ljust(7)
            amount_received1 = str(tx.get('payment1', '')).ljust(7)
            payee2 = str(tx.get('payee2', '')).ljust(7)
            amount_received2 = str(tx.get('payment2', '')).ljust(7)
            status = str(tx['status']).ljust(8)  # Ensure status is included as an integer
            response += f"{tx_id}| {payer}| {amount}| {payee1}| {amount_received1}| {payee2}| {amount_received2}| {status}\n"
        serverSocket.sendto(response.encode(), clientAddress)



    else:
        serverSocket.sendto('Invalid command.'.encode(), clientAddress)
