import config
from hub import Hub

hub = Hub(
    solar_temp = None,
    tank_temp = None,
    tank_target_temp = config.TANK_TARGET_TEMP,
    pump = False,
    mode = 'auto',
)

from internet import Internet
internet = hub.add(Internet)

from temperature import Temperature
hub.add(Temperature)

from display import Display
hub.add(Display, priority=True)

from controller import Controller
hub.add(Controller, priority=True)

from pump import Pump
hub.add(Pump, priority=True)

from components.retain import Retain
hub.add(Retain)

hub.run()
