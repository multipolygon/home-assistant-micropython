from hub import Hub
hub = Hub()
hub.enable = True

from components.retain import Retain
hub.add(Retain)

from alarm import Alarm
hub.add(Alarm)

from sensor import Sensor
hub.add(Sensor)

from battery import Battery
hub.add(Battery)

from deepsleep import Deepsleep
hub.add(Deepsleep)
    
from internet import Internet
hub.add(Internet)

hub.run()
