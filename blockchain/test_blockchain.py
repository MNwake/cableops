from blockchain.blockchain import BlockchainConnector

def test_connection():
    blockchain = BlockchainConnector()
    latest_block = blockchain.get_latest_block()
    print("Latest Block:", latest_block)

if __name__ == "__main__":
    test_connection()
