# blockchain/blockchain.py
from web3 import Web3
from .config import NETWORK_URL


class BlockchainConnector:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum network")

    def get_latest_block(self):
        """Fetch the latest block information."""
        return self.web3.eth.get_block('latest')

    def send_transaction(self, transaction):
        """Placeholder function to send a transaction."""
        pass
