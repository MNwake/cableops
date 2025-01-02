from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Infura URL and private key
infura_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
private_key = os.getenv("PRIVATE_KEY")

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(infura_url))

# Function to test the connection
def test_connection():
    # Check if connected
    if w3.is_connected():
        print("Successfully connected to the Ethereum network")
    else:
        print("Failed to connect to the Ethereum network")
        return

    # Get account details
    account = w3.eth.account.from_key(private_key)
    print(f"Account address: {account.address}")

    # Check account balance
    balance = w3.eth.get_balance(account.address)
    print(f"Account balance: {balance} wei")

    # Fetch latest block number
    latest_block = w3.eth.block_number
    print(f"Latest block number: {latest_block}")

    # Fetch current gas price
    gas_price = w3.eth.gas_price
    print(f"Current gas price: {gas_price} wei")

if __name__ == "__main__":
    test_connection()


