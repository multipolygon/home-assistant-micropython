import config
from hub import Hub

hub = Hub(
    count = -1,
    battery = 100,
)

from internet import Internet
internet = hub.add(Internet)

from counter import Counter
hub.add(Counter)

if config.BATT:
    from components.battery import Battery
    hub.add(Battery)

hub.run()

