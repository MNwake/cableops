from database.cable import Cable
from database.events import Rider, Park

from Model.base_model import BaseScreenModel


class MainScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """
    #test

    def __init__(self, **kw):
        super().__init__(**kw)
        self.parks = Park.objects().all()
        self.cable = Cable.objects().first()
        self.fork_status = self.cable.fork.engaged
        self._rider_on_deck = None
        self.engaged = False
        self.cable.magazine.engaged_callback = self.on_engage
        self.riders_on_carriers = None
        self.riders_checked_in = None
        self.cable.fork.set_model_callback(self.fork_status_changed)  # Set the callback
        self.cable.carrier_pass_callback = self.on_carrier_pass

    @property
    def rider_on_deck(self):
        return self._rider_on_deck

    @rider_on_deck.setter
    def rider_on_deck(self, value):
        self._rider_on_deck = value
        self.cable.rider_on_deck = value
        self.notify_observers('main screen')

    def on_engage(self):
        self.engaged = self.cable.magazine.magazine
        self.notify_observers('main screen')
        
    def fork_status_changed(self, status):
        # Handle the change in fork status
        self.fork_status = status
        self.notify_observers('main screen')

    def on_carrier_pass(self):
        self.rider_on_deck = self.cable.rider_on_deck
        self.update_rider_list()

    def update_rider_list(self, name=None):
        # Initialize an empty set for riders on carriers
        self.riders_on_carriers = set()

        # Check if cable and carriers are set
        if self.cable and self.cable.carriers:
            # Get a set of riders who are currently on carriers
            self.riders_on_carriers = {carrier.rider for carrier in self.cable.carriers if carrier.rider}

        # Initialize an empty list for filtered riders
        filtered_riders = []

        # Check if park and riders_checked_in are set
        if self.cable.park and self.cable.park.riders_checked_in:
            # Filter out these riders from the main rider list
            # Include only riders not in riders_on_carriers
            filtered_riders = [rider for rider in self.cable.park.riders_checked_in if
                               rider not in self.riders_on_carriers]

        # Additional filtering based on the 'text' if provided
        if name:
            text = name.lower()  # Lowercasing for case-insensitive search
            filtered_riders = [rider for rider in filtered_riders if text in rider.full_name.lower()]

        self.riders_checked_in = filtered_riders
        # Notify observers about the update
        self.notify_observers('main screen')


