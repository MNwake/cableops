from blockchain.cablecoin_contract import CableCoinContract

import os
from blockchain.cablecoin_contract import CableCoinContract


if __name__ == "__main__":
    cable_coin = CableCoinContract()
    recipient_address = "0x0AEab61ea8626845600Bbc16B7DB61c84103303d"  # Replace with a recipient's address

    amount_to_transfer = 100  # Amount in CableCoin
    scaled_amount = int(amount_to_transfer * (10 ** 18))  # Scale amount to 18 decimals

    # Get the sender account
    sender_address = cable_coin.w3.eth.account.from_key(os.getenv("PRIVATE_KEY")).address

    # Check recipient balance before the transfer
    print(f"Recipient Balance Before Transfer: {cable_coin.get_balance(recipient_address)}")

    # Perform the first transfer
    print("Initiating first transfer...")
    tx_hash_1 = cable_coin.transfer(recipient_address, scaled_amount)
    print(f"First Transfer Transaction Hash: {tx_hash_1.hex()}")

    # Wait for the first transaction to be mined
    print("Waiting for the first transaction to be mined...")
    receipt_1 = cable_coin.w3.eth.wait_for_transaction_receipt(tx_hash_1)
    print(f"First Transaction Receipt: {receipt_1}")

    # Perform the second transfer with a new nonce
    print("Initiating second transfer...")
    tx_hash_2 = cable_coin.transfer(recipient_address, scaled_amount)
    print(f"Second Transfer Transaction Hash: {tx_hash_2.hex()}")

    # Wait for the second transaction to be mined
    print("Waiting for the second transaction to be mined...")
    receipt_2 = cable_coin.w3.eth.wait_for_transaction_receipt(tx_hash_2)
    print(f"Second Transaction Receipt: {receipt_2}")

    # Check recipient balance after the transfers
    print(f"Recipient Balance After Transfers: {cable_coin.get_balance(recipient_address)}")
