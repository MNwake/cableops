import sys
import time
from solcx import compile_source, install_solc, get_installed_solc_versions, set_solc_version
from web3 import Web3
import os
from dotenv import load_dotenv
from web3.exceptions import TransactionNotFound, TimeExhausted

load_dotenv()  # Load environment variables

class CableCoinContract:
    _instance = None  # Class-level attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        print('new instance')
        if cls._instance is None:
            cls._instance = super(CableCoinContract, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        print('init')
        if hasattr(self, "initialized"):
            return
        self.initialized = True
        infura_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum network")

        self.configure_solc()
        self.abi, self.bytecode = self.compile_contract()
        self.contract_address = os.getenv("CABLECOIN_ADDRESS")
        if not self.contract_address:
            initial_supply = 1000000
            self.contract_address = self.deploy_contract(initial_supply)
            self.save_contract_address(self.contract_address)

        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        print(f"Using contract at address: {self.contract_address}")


    def configure_solc(self):
        """Set up solc based on the operating system."""
        if sys.platform == 'linux':  # For Raspberry Pi
            solc_binary = os.getenv("SOLCX_BINARY", "/usr/local/bin/solc")
            print(f"Using custom solc binary on Raspberry Pi: {solc_binary}")
        elif sys.platform == 'darwin':  # For macOS
            installed_versions = get_installed_solc_versions()
            if "0.8.20" not in installed_versions:  # Install if not already installed
                print("Installing solc 0.8.20...")
                install_solc("0.8.20")
            set_solc_version("0.8.20")  # Explicitly set the installed version
            print("Using solc 0.8.20 on macOS")

    def compile_contract(self):
        # Get the current directory of the script
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the contract file
        contract_path = os.path.join(base_dir, "contracts", "CableCoin.sol")
        print(f"Contract path: {contract_path}")

        # Read the contract source code
        with open(contract_path, "r") as file:
            source_code = file.read()

        # Dynamically determine paths based on the platform
        if sys.platform == 'darwin':  # macOS
            base_path = "/Users/theokoester/dev/projects/python/CWA/cableops/server"
            include_path = f"{base_path}/node_modules"
        elif sys.platform == 'linux':  # Raspberry Pi
            base_path = "/home/theokoester/dev/cableops/server"
            include_path = f"{base_path}/node_modules"

        # Allow paths must include both base and node_modules
        allow_paths = f"{base_path}:{include_path}"
        print(f"Base path: {base_path}")
        print(f"Include path: {include_path}")
        print(f"Allow paths: {allow_paths}")

        # Compile the contract
        compiled_sol = compile_source(
            source_code,
            output_values=["abi", "bin"],
            allow_paths=allow_paths,
            base_path=base_path
        )

        # Debug compiled contracts
        print("Compiled contracts:", compiled_sol.keys())

        # Use the correct contract name from the compiled output
        contract_name = "<stdin>:CableCoin"  # Adjusted based on debug output
        if contract_name not in compiled_sol:
            raise KeyError(f"Contract '{contract_name}' not found in compiled contracts.")

        self.abi = compiled_sol[contract_name]["abi"]
        self.bytecode = compiled_sol[contract_name]["bin"]
        return self.abi, self.bytecode

    def deploy_contract(self, initial_supply):
        print('Deploying contract...')
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        balance = self.w3.eth.get_balance(account.address)
        print(f"Account balance: {balance} wei")

        CableCoin = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        nonce = self.w3.eth.get_transaction_count(account.address)
        gas_price = self.w3.eth.gas_price + 10000000

        try:
            transaction = CableCoin.constructor(initial_supply).build_transaction({
                "from": account.address,
                "nonce": nonce,
                "gas": 2000000,
                "gasPrice": gas_price,
            })
            signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"Transaction sent with hash: {tx_hash.hex()}")
            print("Waiting for transaction to be mined...")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=5)
            contract_address = tx_receipt.contractAddress
            print(f"Contract deployed at address: {contract_address}")
            return contract_address
        except Exception as e:
            print(f"Error deploying contract: {e}")
            raise e

    def save_contract_address(self, address):
        with open(".env", "a") as env_file:
            env_file.write(f"\nCABLECOIN_ADDRESS={address}")

    def get_total_supply(self):
        return self.contract.functions.totalSupply().call()

    def get_balance(self, address):
        balance_wei = self.contract.functions.balanceOf(address).call()
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return balance_eth

    def transfer(self, to_address, amount):
        print('Initiating transfer')
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

        # Fetch base fee and priority fee
        base_fee = self.w3.eth.get_block("pending").baseFeePerGas
        priority_fee = self.w3.eth.max_priority_fee  # Fetch priority fee dynamically

        # Calculate effective gas price
        gas_price = base_fee + priority_fee
        print(f"Calculated Gas Price: {gas_price}")

        # Estimate Gas
        estimated_gas = self.contract.functions.transfer(to_address, amount).estimate_gas({"from": account.address})
        print(f"Estimated Gas: {estimated_gas}")

        # Build transaction
        transaction = self.contract.functions.transfer(to_address, amount).build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": estimated_gas + 10000,  # Add buffer to estimated gas
            "maxFeePerGas": gas_price,
            "maxPriorityFeePerGas": priority_fee,
        })

        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent with hash: {tx_hash.hex()}")

        # Wait for the transaction receipt
        print("Waiting for the transaction to be mined...")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        actual_gas_used = receipt.gasUsed
        print(f"Transaction mined. Gas Used: {actual_gas_used}")
        print(f"Gas Difference (Limit - Used): {estimated_gas + 10000 - actual_gas_used}")

        return tx_hash

    # New Methods
    def mint_tokens(self, amount):
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        transaction = self.contract.functions.mint(amount).build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def burn_tokens(self, amount):
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        transaction = self.contract.functions.burn(amount).build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def pause_contract(self):
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        transaction = self.contract.functions.pause().build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def resume_contract(self):
        account = self.w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
        transaction = self.contract.functions.unpause().build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed_tx = self.w3.eth.account.sign_transaction(transaction, os.getenv("PRIVATE_KEY"))
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash

    def get_owner_balance(self, owner_address):
        """Get the owner's CableCoin balance."""
        return self.get_balance(owner_address)

    @property
    def network_name(self):
        chain_id = self.w3.eth.chain_id
        # Map chain IDs to network names
        network_map = {
            1: "Ethereum Mainnet",
            3: "Ropsten",
            4: "Rinkeby",
            5: "Goerli",
            42: "Kovan",
            11155111: "Sepolia"
        }
        return network_map.get(chain_id, "Unknown Network")

