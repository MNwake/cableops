# The screen's dictionary contains the objects of the models and controllers
# of the screens of the application.

from Model.main_screen import MainScreenModel
from Controller.main_screen import MainScreenController
from Model.cable_coin_screen import CableCoinScreenModel
from Controller.cable_coin_screen import CableCoinScreenController
from Model.cable_ops_screen import CableOpsScreenModel
from Controller.cable_ops_screen import CableOpsScreenController

screens = {
    'cable coin': {
        'model': CableCoinScreenModel,
        'controller': CableCoinScreenController,
    },
    'cable ops': {
        'model': CableOpsScreenModel,
        'controller': CableOpsScreenController,
    },
    'main screen': {
        'model': MainScreenModel,
        'controller': MainScreenController,
    },
}