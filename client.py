from socket import *

# Define transaction status constants
STATUS_TEMPORARY = 1
STATUS_CONFIRMED = 2
STATUS_REJECTED = 3

transactions = []

highest_ids = {}  # Dictionary to store the highest ID for each user

def get_highest_transaction_id(username):
    highest_id = highest_ids.get(username, 0)  # Get the highest ID for the user
    for tx in transactions:
        if tx['payer'] == username:
            highest_id = max(highest_id, tx['tx_id'])
    print(f"Highest transaction ID for {username}: {highest_id}")
    highest_ids[username] = highest_id  # Update the highest ID for the user
    return highest_id

def generate_transaction_id(username):
    user_id_mapping = {'A': 100, 'B': 200, 'C': 300, 'D': 400}
    highest_id = get_highest_transaction_id(username)
    if highest_id == 0:
        new_id = user_id_mapping[username]
        print(f"New transaction ID for {username}: {new_id}")
        transaction_id = new_id
    else:
        new_id = highest_id + 1
        print(f"New transaction ID for {username}: {new_id}")
        transaction_id = new_id

    # Append the transaction to the transactions list
    transactions.append({
        'tx_id': transaction_id,
        'payer': username,
        'status': STATUS_TEMPORARY
    })

    return transaction_id

def send_temporary_transaction(username, transaction):
    server_name = 'localhost'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    transaction_str = f'TX tx_id={transaction["tx_id"]} amount={transaction["amount"]} payer={username} payee1={transaction["payee1"]} payment1={transaction["payment1"]} payee2={transaction["payee2"]} payment2={transaction["payment2"]} status={transaction["status"]}'
    client_socket.sendto(transaction_str.encode(), (server_name, server_port))
    response, _ = client_socket.recvfrom(2048)
    client_socket.close()
    response_parts = response.decode().split()
    if len(response_parts) >= 2 and response_parts[0] == 'TX':
        if response_parts[1] == 'confirmed.':
            transaction['status'] = 'confirmed'
        elif response_parts[1] == 'rejected.':
            transaction['status'] = 'rejected'
    return response.decode()


# Authentication code, client uses UDP as per assignment requirements
def authenticate(username, password):
    server_name = 'localhost'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(f'LOGIN {username} {password}'.encode(), (server_name, server_port))
    response, _ = client_socket.recvfrom(2048)
    client_socket.close()
    return response.decode()

def validate_transaction(username, amount):
    server_name = 'localhost'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(f'VALIDATE {username} {amount}'.encode(), (server_name, server_port))
    response, _ = client_socket.recvfrom(2048)
    client_socket.close()
    return response.decode()

def update_transaction_status(tx_id, status):
    for tx in transactions:
        if tx['tx_id'] == tx_id:
            tx['status'] = status
            break

# Modify the fetch_transactions function to handle balance and transaction list separately
def fetch_transactions(username):
    server_name = 'localhost'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(f'TX_LIST {username}'.encode(), (server_name, server_port))
    response, _ = client_socket.recvfrom(2048)
    client_socket.close()
    response_parts = response.decode().split('\n', 1)
    balance = response_parts[0]
    transaction_list_response = response_parts[1] if len(response_parts) > 1 else ""
    return balance, transaction_list_response

def display_transactions(transactions):
    print("Transactions:")
    if not transactions:
        print("No transactions found!")
    else:
        print("TX ID  | Payer | Amount | Payee1 | Amount | Payee2 | Amount | Status")
        print("-" * 68)  # Adding a line to separate header and data
        for tx in transactions:
            status = ''
            if tx['status'] == STATUS_TEMPORARY:
                status = 'temporary'
            elif tx['status'] == STATUS_CONFIRMED:
                status = 'confirmed'
            elif tx['status'] == STATUS_REJECTED:
                status = 'rejected'

            tx_id = str(tx['tx_id']).ljust(6)
            payer = tx['payer'].ljust(6)
            amount = str(tx['amount']).ljust(7)
            payee1 = tx['payee1'].ljust(7)
            amount_received1 = str(tx.get('payment1', '')).ljust(7)
            payee2 = str(tx.get('payee2', '')).ljust(7)
            amount_received2 = str(tx.get('payment2', '')).ljust(7)
            status = status.ljust(8)  # Ensure status is included as an integer

            print(f"{tx_id}| {payer}| {amount}| {payee1}| {amount_received1}| {payee2}| {amount_received2}| {status}")

def main():
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")

        auth_response = authenticate(username, password)

        if "successful" in auth_response:
            print("\nLogin successful!")
            break  # Break out of the authentication loop upon successful login
        else:
            print(auth_response)
            while True:
                choice = input("Choose an option:\n1. Retry entering username and password\n2. Quit\nChoice: ")
                if choice == '1':
                    break  # Break out of the retry loop to enter username and password again
                elif choice == '2':
                    print("Exiting program.")
                    return  # Exit the program
                else:
                    print("Invalid choice. Please enter 1 or 2.")

    # Fetch and display transaction list from server
    balance, transaction_list_response = fetch_transactions(username)
    print(f"\nBalance: {balance}")
    print("\nReceived transaction list from server:")
    print(transaction_list_response)

    while True:
        print("\nMenu:")
        print("1. Make a transaction")
        print("2. Fetch and display the list of transactions")
        print("3. Quit the program")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nTransaction Creation:")
            amount = float(input("How much do you transfer? "))

            payee_options = {
                'A': ['B', 'C', 'D'],
                'B': ['A', 'C', 'D'],
                'C': ['A', 'B', 'D'],
                'D': ['A', 'B', 'C']
            }

            print("Who will be Payee1?")
            for index, user in enumerate(payee_options[username], start=1):
                print(f"{index}. {user}")

            payee1_option = int(input("Enter your choice: "))
            payee1 = payee_options[username][payee1_option - 1]

            payee_options_without_payee1 = payee_options[username][:]
            payee_options_without_payee1.remove(payee1)

            amount_to_payee1 = float(input(f"How much do you want to send to {payee1}? "))
            amount_to_payee2 = amount - amount_to_payee1
            payee2 = None

            if amount_to_payee2 > 0:
                print("Who will be Payee2?")
                for index, user in enumerate(payee_options_without_payee1, start=1):
                    print(f"{index}. {user}")

                payee2_option = int(input("Enter your choice: "))
                payee2 = payee_options_without_payee1[payee2_option - 1]

            tx_id = generate_transaction_id(username)

            transaction = {
                'tx_id': tx_id,
                'amount': amount,
                'payee1': payee1,
                'payment1': amount_to_payee1,
                'payee2': payee2,
                'payment2': amount_to_payee2,
                'status': STATUS_TEMPORARY  # Marking the transaction as temporary
            }

            # Send the temporary transaction to the server for processing
            response = send_temporary_transaction(username, transaction)
            print("Received response from server:", response)
            if "confirmed" in response:
                update_transaction_status(transaction['tx_id'], STATUS_CONFIRMED)
            else:
                update_transaction_status(transaction['tx_id'], STATUS_REJECTED)

            if "confirmed" in response:
                update_transaction_status(transaction['tx_id'], STATUS_CONFIRMED)
                if payee2:
                    print("\n")
                    print(f"{transaction['tx_id']}: {username} transferred {int(transaction['amount'])}BTC. {transaction['payee1']} received {int(transaction['payment1'])}BTC. {transaction['payee2']} received {int(transaction['payment2'])}BTC")
                else:
                    print("\n")
                    print(f"{transaction['tx_id']}: {username} transferred {int(transaction['amount'])}BTC. {transaction['payee1']} received {int(transaction['payment1'])}BTC.")
            else:
                update_transaction_status(transaction['tx_id'], STATUS_REJECTED)


        elif choice == '2':
            # Fetching and displaying balance and transaction list
            balance, transaction_list_response = fetch_transactions(username)
            print(f"\nBalance: {balance}")
            print("\nReceived transaction list from server:")
            print(transaction_list_response)
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
