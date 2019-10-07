from lib.home_assistant.binary_sensor import BinarySensor
  
class SoundBinarySensor(BinarySensor):
    DEVICE_CLASS = "sound" # On means sound detected, Off means no sound (clear)
