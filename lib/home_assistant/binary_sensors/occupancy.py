from lib.home_assistant.binary_sensor import BinarySensor
  
class OccupancyBinarySensor(BinarySensor):
    DEVICE_CLASS = "occupancy" # On means occupied, Off means not occupied (clear)
