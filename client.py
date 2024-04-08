from socket import *

# authentication code, client uses UDP as per assignment requirements
def authenticate(username, password):
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(f'LOGIN {username} {password}'.encode(), (serverName, serverPort))
    response, _ = clientSocket.recvfrom(2048)
    clientSocket.close()
    return response.decode()

def validate_transaction(username, amount):
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(f'VALIDATE {username} {amount}'.encode(), (serverName, serverPort))
    response, _ = clientSocket.recvfrom(2048)
    clientSocket.close()
    return response.decode()

def send_transaction(transaction):
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    # Convert transaction dictionary to a string representation for sending
    transaction_str = f'TX {transaction["tx_id"]} {transaction["amount"]} {transaction["payee1"]} {transaction["payment1"]} {transaction["payee2"]} {transaction["payment2"]}'
    clientSocket.sendto(transaction_str.encode(), (serverName, serverPort))
    response, _ = clientSocket.recvfrom(2048)
    clientSocket.close()
    return response.decode()

# displays list of transactions for logged in user, tx = transaction
def display_transactions(transactions):
    print("Transactions:")
    if not transactions:
        print("No transactions found!")
    else:
        print("TX ID | Payer | Amount | Payee1 | Amount | Payee2 | Amount")
        for tx in transactions:
            print(f"{tx['tx_id']} | {tx['payer']} | {tx['amount']} | {tx['payee1']} | {tx['amount_received1']} | {tx.get('payee2', '')} | {tx.get('amount_received2', '')}")

# prompts username and password, then sends to server for authentication
# once authenticated, displays login success message, balance, and tx list
def main():
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    auth_response = authenticate(username, password)
    print("\nReceived response from server:", auth_response)  # debug statement

    #if authentication success, display menu
    if "successful" in auth_response:
        while True:
            print("\nMenu:")
            print("1. Make a transaction")
            print("2. Fetch and display the list of transactions")
            print("3. Quit the program")
            choice = input("Enter your choice: ")

            if choice == '1':
                # Transaction creation
                print("\nTransaction Creation:")
                while True:
                    amount = float(input("How much do you transfer? "))
                    # Validate transaction amount with server
                    validate_response = validate_transaction(username, amount)
                    if "exceeds balance" in validate_response:
                        print("Transaction amount exceeds your balance. Please enter a lower amount.")
                    else:    
                        break
                
                # Dictionary to map usernames to their respective payee options
                payee_options = {
                    'A': ['B', 'C', 'D'],
                    'B': ['A', 'C', 'D'],
                    'C': ['A', 'B', 'D'],
                    'D': ['A', 'B', 'C']
                }

                # Prompt user to select Payee1
                print("Who will be Payee1?")
                for index, user in enumerate(payee_options[username], start=1):
                    print(f"{index}. {user}")

                payee1_option = int(input("Enter your choice: "))
                payee1 = payee_options[username][payee1_option - 1]

                # Remove Payee1 from the list of payee options for Payee2
                payee_options_without_payee1 = payee_options[username][:]
                payee_options_without_payee1.remove(payee1)

                # Calculate amount to Payee1
                amount_to_payee1 = float(input("How much do you want to send to Payee1? "))
                while amount_to_payee1 > amount:
                    print("Amount exceeds total transaction amount. Please enter a lower amount.")
                    amount_to_payee1 = float(input("How much do you want to send to Payee1? "))
                
                # Calculate amount to Payee2
                amount_to_payee2 = amount - amount_to_payee1
                payee2 = None
                
                # If there's still remaining amount, ask for Payee2
                if amount_to_payee2 > 0:
                    print("Who will be Payee2?")
                    for index, user in enumerate(payee_options_without_payee1, start=1):
                        print(f"{index}. {user}")

                    payee2_option = int(input("Enter your choice: "))
                    payee2 = payee_options_without_payee1[payee2_option - 1]

                # TX id assignment based on user
                tx_id = (ord(username) - 65 + 1) * 100
                
                # Create temporary transaction
                transaction = {
                    'tx_id': tx_id,
                    'payer': username,
                    'amount': amount,
                    'payee1': payee1,
                    'payment1': amount_to_payee1,
                    'payee2': payee2,
                    'payment2': amount_to_payee2
                }

                # Send the temporary transaction to the server for processing
                response = send_transaction(transaction)
                print("Received response from server:", response)
                # Handle server responses accordingly
                
                 # Display transaction details based on number of payees
                if payee2:
                    print("\n")
                    print(f"{transaction['tx_id']}: {transaction['payer']} transferred {int(transaction['amount'])}BTC. {transaction['payee1']} received {int(transaction['payment1'])}BTC. {transaction['payee2']} received {int(transaction['payment2'])}BTC")
                else:
                    print("\n")
                    print(f"{transaction['tx_id']}: {transaction['payer']} transferred {int(transaction['amount'])}BTC. {transaction['payee1']} received {int(transaction['payment1'])}BTC.")


            elif choice == '2':
                # Fetch and display transaction list from server
                pass

            elif choice == '3':
                print("Exiting program.")
                break

            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    #if authentication fails, prompt username/password retry
    else:
        print(auth_response)
        while True:
            choice = input("Choose an option:\n1. Enter username and password again\n2. Quit\nChoice: ")
            if choice == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")
                auth_response = authenticate(username, password)
                print("Received response from server:", auth_response)  # Debugging statement

            elif choice == '2':
                print("Exiting program.")
                break

            else:
                print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
