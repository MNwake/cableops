from Model.base_model import BaseScreenModel


class CableCoinScreenModel(BaseScreenModel):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.home_address = '0x5DEF65BAA081EF591115212a868a4FBB386b6697'
        self._balance = None
        self._contract_address = None
        self._total_supply = None
        self._pwner_balance = None
        self._network_name = None

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self._balance = value
        self.notify_observers('cable coin')

    @property
    def contract_address(self):
        return self._contract_address

    @contract_address.setter
    def contract_address(self, value):
        self._contract_address = value
        self.notify_observers('cable coin')

    @property
    def total_supply(self):
        return self._total_supply

    @total_supply.setter
    def total_supply(self, value):
        self._total_supply = value
        self.notify_observers('cable coin')

    @property
    def owner_balance(self):
        return self._total_supply

    @owner_balance.setter
    def owner_balance(self, value):
        self._pwner_balance = value
        self.notify_observers('cable coin')

    @property
    def network_name(self):
        return self._network_name

    @network_name.setter
    def network_name(self, value):
        self._network_name = value
        self.notify_observers('cable coin')