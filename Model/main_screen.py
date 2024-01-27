from Cable.cable import Cable
from Database.rider import Rider

from Model.base_model import BaseScreenModel


class MainScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """


    def __init__(self, **kw):
        super().__init__(**kw)
        self.cable = Cable()
        self.fork_status = self.cable.fork.engaged
        self.riders = Rider.objects().all()
        self._riders_list = self.riders
        self._rider_on_deck = None
        self.engaged = False
        self.cable.magazine.engaged_callback = self.on_engage
        self.riders_on_carriers = None
        self.cable.fork.set_model_callback(self.fork_status_changed)  # Set the callback


    @property
    def rider_on_deck(self):
        return self._rider_on_deck

    @rider_on_deck.setter
    def rider_on_deck(self, value):
        self._rider_on_deck = value
        self.cable.rider_on_deck = value
        self.notify_observers('main screen')

    @property
    def riders_list(self):
        return self._riders_list

    @riders_list.setter
    def riders_list(self, value):
        self._riders_list = value
        self.notify_observers('main screen')

    def on_engage(self):
        self.engaged = self.cable.magazine.magazine
        self.notify_observers('main screen')
        
    def fork_status_changed(self, status):
        # Handle the change in fork status
        self.fork_status = status
        self.notify_observers('main screen')

    def update_rider_list(self, text=None):
        # Get a set of riders who are currently on carriers
        self.riders_on_carriers = {carrier.rider for carrier in self.cable.carriers if carrier.rider}

        # Filter out these riders from the main rider list
        filtered_riders = [rider for rider in self.riders if rider not in self.riders_on_carriers]

        # Additional filtering based on the 'text' if provided
        if text:
            text = text.lower()  # Lowercasing for case-insensitive search
            filtered_riders = [rider for rider in filtered_riders if text in rider.full_name.lower()]

        self.riders_list = filtered_riders

        # Notify observers about the update
        self.notify_observers('main screen')
