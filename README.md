# Simple Bitcoin Network (UDP-Based)

This is a lightweight Python project that simulates a Bitcoin-style transaction network using UDP sockets. It features a client-server architecture where users can log in, check balances, initiate transactions, and view transaction histories — all over connectionless communication.

> ⚠ Not a real blockchain — this was built as part of a networking course to demonstrate concepts like UDP communication, user state tracking, and basic transaction validation.

---

## Features

- Simple user login/authentication  
- Account balances and validation  
- Create transactions with one or two payees  
- Stateless communication via UDP sockets  
- Human-readable transaction log with status tracking (`temporary`, `confirmed`, `rejected`)  
- Fetch and display user-specific transaction history  

---

## File Overview

| File        | Description |
|-------------|-------------|
| `server.py` | Listens for incoming UDP packets, authenticates users, processes and validates transactions, and maintains user states. |
| `client.py` | Handles user input, formats transaction data, sends requests to the server, and displays results to the user. |

---

## How It Works

- All communication happens over **UDP sockets** (port `12000`).
- Users `A`, `B`, `C`, and `D` each start with 10 BTC and can:
  - Authenticate with a username/password pair
  - Send BTC to one or two other users
  - Validate that they have sufficient balance before submitting
  - Retrieve a summary of all transactions involving them
- The system simulates transaction "states" for demonstration purposes:
  - `temporary`: transaction received but not yet confirmed
  - `confirmed`: validated and processed successfully
  - `rejected`: failed due to insufficient balance

---

## Technologies

- Python 3
- `socket` module (`UDP` protocol)
- Command-line interface (CLI)
- No third-party dependencies

---

## Getting Started

### Prerequisites
- Python 3.x

### Running the Project

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Run the client in a separate terminal:**
   ```bash
   python client.py
   ```

3. **Login with one of the sample users:**
   ```
   Username: A
   Password: A
   ```

4. Follow the prompts to create transactions or view your balance.

---

## Sample Users

| Username | Password | Starting Balance |
|----------|----------|------------------|
| A        | A        | 10 BTC           |
| B        | B        | 10 BTC           |
| C        | C        | 10 BTC           |
| D        | D        | 10 BTC           |

---

## Learning Goals

This project was built to demonstrate:
- UDP communication in a client-server model
- Basic authentication and validation logic
- Multi-user transaction state handling
- CLI data input/output formatting
- Socket programming fundamentals

---

## Notes

- Because it uses **UDP**, there is no built-in connection validation or packet loss recovery — it’s intentionally fragile to highlight stateless communication.
- All data is stored **in-memory**, and will reset when the program restarts.
- Not suitable for production or real-world financial simulation.
