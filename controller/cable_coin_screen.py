
from View.CableCoinScreen.cable_coin_screen import CableCoinScreenView
from blockchain.cablecoin_contract import CableCoinContract


class CableCoinScreenController:
    def __init__(self, model):
        self.model = model
        self.view = CableCoinScreenView(controller=self, model=self.model)
        self.contract = CableCoinContract()
        print(f"Deployed Contract Address: {self.contract.contract_address}")

        self.model.contract_address = self.contract.contract_address
        self.model.network_name = self.contract.network_name
    def get_view(self) -> CableCoinScreenView:
        return self.view

    def get_balance(self):
        self.model.balance = self.contract.get_balance(self.model.home_address)

    def get_total_supply(self):
        self.model.total_supply = self.contract.get_total_supply()

    def get_owner_balance(self):
        """Fetch the owner's CableCoin balance from the contract."""
        self.model.owner_balance = self.contract.get_owner_balance(self.model.home_address)

    def initiate_transfer(self, recipient, amount):
        try:
            amount_in_wei = int(float(amount) * 10 ** 18)  # Convert to wei if using Ether units
            tx_hash = self.contract.transfer(recipient, amount_in_wei)
            return {"status": "success", "message": f"Transfer successful with tx hash: {tx_hash.hex()}"}
        except ValueError:
            return {"status": "error", "message": "Invalid amount entered. Please enter a numeric value."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred during transfer: {e}"}

    def mint_tokens(self, amount):
        tx_hash = self.contract.mint_tokens(amount)
        print(f"Minting initiated with tx hash: {tx_hash}")

    def burn_tokens(self, amount):
        tx_hash = self.contract.burn_tokens(amount)
        print(f"Burning initiated with tx hash: {tx_hash}")

    def pause_contract(self):
        tx_hash = self.contract.pause_contract()
        print(f"Contract paused with tx hash: {tx_hash}")

    def resume_contract(self):
        tx_hash = self.contract.resume_contract()
        print(f"Contract resumed with tx hash: {tx_hash}")

