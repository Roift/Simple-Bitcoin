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
                # todo: transaction creation
                pass
            elif choice == '2':
                # todo: fetch and display tx list from server
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