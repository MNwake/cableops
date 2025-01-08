from pprint import pprint

from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty
from kivymd.uix.button import MDButtonIcon
from kivymd.uix.dialog import MDDialog

from View.base_screen import BaseScreenView
from blockchain.cablecoin_contract import CableCoinContract


class CableCoinScreenView(BaseScreenView):
    balance = StringProperty()
    network_name = StringProperty()
    total_supply = StringProperty()
    contract_address = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Cable Coin"
        self.dialog = None

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
        self.balance = str(self.model.balance)
        self.total_supply = str(self.model.total_supply)
        self.contract_address = str(self.model.contract_address)
        self.network_name = str(self.model.network_name)

    def on_enter(self, *args):
        self.controller.get_owner_balance()
        self.controller.get_balance()
        self.controller.get_total_supply()

    def copy_contract_address(self):
        """
        Copy the contract address to the clipboard.
        """
        if self.contract_address:
            Clipboard.copy(self.contract_address)
            print("Contract address copied to clipboard.")

    def initiate_transfer(self):
        response = self.controller.initiate_transfer(self.ids.transfer_address.text, self.ids.transfer_amount.text)

        if response["status"] == "success":
            # Clear text fields if the transfer was successful
            self.ids.transfer_address.text = ""
            self.ids.transfer_amount.text = ""
            # Notify the user of the success
        else:
            # Show an error message to the user
            self.ids.transfer_address.text = "error"
            self.ids.transfer_amount.text = response["message"]

