from socket import *

# Server configuration
server_port = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
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
def find_user(username):
    for user in users:
        if user['username'] == username:
            return user
    return None

# Process transaction
def process_transaction(transaction):
    payer = transaction['payer']
    amount = transaction['amount']
    payee1 = transaction['payee1']
    user = find_user(payer)

    if not user or user['balance'] < amount:
        print(f'Received a transaction request from {payer}. Insufficient balance. Transaction rejected.')
        return f'TX {transaction["tx_id"]} rejected. Insufficient balance. Your current balance is {user["balance"]} BTC.'

    user['balance'] -= amount

    payee = find_user(payee1)
    if payee:
        payee['balance'] += amount

    transactions.append(transaction)

    print(f'Transaction {transaction["tx_id"]} confirmed. Balance updated for {payer} and {payee1}.')
    transaction['status'] = 'confirmed'
    return f'TX {transaction["tx_id"]} confirmed. Your current balance is {int(user["balance"])} BTC.'

def process_temporary_transaction(transaction):
    payer = transaction['payer']
    amount = transaction['amount']
    user = find_user(payer)

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
    user_balance = None
    for user in users:
        if user['username'] == username:
            user_balance = user['balance']
            break
    for transaction in transactions:
        if transaction['payer'] == username or transaction['payee1'] == username or transaction.get('payee2') == username:
            user_transactions.append(transaction)
    return user_balance, user_transactions

while True:
    message, client_address = server_socket.recvfrom(2048)
    message_parts = message.decode().split()

    if len(message_parts) < 2:
        server_socket.sendto('Invalid request format.'.encode(), client_address)
        continue

    command = message_parts[0].upper()

    if command == 'LOGIN':
        username = message_parts[1]
        password = message_parts[2]
        user = find_user(username)
        
        if not user or user['password'] != password:
            print(f'Authentication request received from {username}. Authentication failed.')
            server_socket.sendto('Invalid username or password.'.encode(), client_address)
            continue

        response = f'Login successful!\nBalance: {int(user["balance"])}'
        print(f'{username} is authenticated.')
        server_socket.sendto(response.encode(), client_address)

    elif command == 'VALIDATE':
        username = message_parts[1]
        amount = float(message_parts[2])
        user = find_user(username)
        if not user or user['balance'] < amount:
            print(f'Validation request received from {username}. Transaction amount exceeds balance. Validation failed.')
            server_socket.sendto('Transaction amount exceeds balance.'.encode(), client_address)
        else:
            print(f'Validation request received from {username}. Transaction amount is valid.')
            server_socket.sendto('Transaction amount is valid.'.encode(), client_address)

    elif command == 'TX':
        transaction = {}
        for part in message_parts[1:]:
            if '=' in part:
                key, value = part.split('=')
                transaction[key] = value

        if 'tx_id' not in transaction:
            server_socket.sendto('Transaction ID is missing.'.encode(), client_address)
            continue

        try:
            tx_id = int(transaction['tx_id'])
        except ValueError:
            server_socket.sendto('Invalid transaction ID.'.encode(), client_address)
            continue

        amount = float(transaction['amount'])
        payer = transaction['payer']
        payee1 = transaction['payee1']
        amount_to_payee1 = float(transaction['payment1']) if 'payment1' in transaction else None
        payee2 = transaction['payee2'] if 'payee2' in transaction else None
        amount_to_payee2 = float(transaction['payment2']) if 'payment2' in transaction else None
        status = transaction['status'] if 'status' in transaction else 'temporary'  # Set status here if not received from client

        if amount_to_payee1 is not None and (amount_to_payee1 < 0 or amount_to_payee1 > amount):
            server_socket.sendto('Invalid payment amount for Payee1.'.encode(), client_address)
            continue
        if payee2 is not None and (amount_to_payee2 is None or amount_to_payee2 < 0 or amount_to_payee2 > (amount - amount_to_payee1)):
            server_socket.sendto('Invalid payment amount for Payee2.'.encode(), client_address)
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
            response = process_transaction(transaction)

        server_socket.sendto(response.encode(), client_address)


    elif command == 'TX_LIST':
        username = message_parts[1]
        user_balance, user_transactions = get_user_transactions(username)
        if user_balance is None:
            server_socket.sendto('User not found.'.encode(), client_address)
        else:
            response = f"{user_balance}BTC\n"
            response += "TX ID  | Payer | Amount | Payee1 | Amount | Payee2 | Amount | Status\n"
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
            server_socket.sendto(response.encode(), client_address)
    else:
        server_socket.sendto('Invalid command.'.encode(), client_address)
