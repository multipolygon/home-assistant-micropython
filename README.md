# MicroPython IoT Devices for Home Assistant

## Project Details

This project is under active development.

The aim is to create a framework for registering ESP8266 and ESP32 devices (eg sensors and lights) with [Home Assistant](https://www.home-assistant.io) via [MQTT Discovery](https://www.home-assistant.io/docs/mqtt/discovery) protocol.

The MQTT Discovery lib is mostly stable and could be used in any project:

- [lib/home_assistant](./lib/home_assistant)

For example usage see:

- [./build/py/pir_security_light/](./build/py/pir_security_light/)
- [./build/py/counter_sensor/](./build/py/counter_sensor/)
- [./build/py/light/](./build/py/light/)

## Install Notes

### Python

https://pipenv.readthedocs.io/en/latest/

    pip install --user pipenv
    
or

    brew install pipenv

then

    pipenv install

#### Resources

https://github.com/espressif/esptool

https://github.com/wendlers/mpfshell

http://micropython.org/webrepl/

### USB

Give user access to /dev/ttyUSB0:

    sudo usermod -a -G dialout $USER
    sudo usermod -a -G tty $USER
    sudo reboot

### ESP8266

#### 4MB

Downloads: https://micropython.org/download#esp8266

Erase:

    PORT=/dev/tty.usbserial-1420
    pipenv run python -m esptool --port $PORT erase_flash

Flash:

    pipenv run python -m esptool --port $PORT --baud 115200 write_flash 0 bin/esp8266-$VERSION.bin

#### 16MB

Instructions from here:

https://github.com/micropython/micropython/issues/2335#issuecomment-520210822

Erase:

    pipenv run python -m esptool --port $PORT --after no_reset --baud 460800 erase_flash

Flash `esp_init_data_default.bin`:

    pipenv run python -m esptool --port $PORT write_flash 0xffc000 bin/esp_init_data_default.bin

Flash to the 16mb ESP8266 module (eg. Lolin D1 Mini Pro) for your version of `esp8266-*.bin`:

    pipenv run python -m esptool --port $PORT --baud 460800 write_flash -fm dio -fs 16MB 0x00000 bin/esp8266-$VERSION.bin

### ESP32

Downloads: https://micropython.org/download#esp32

    pipenv run python -m esptool --port $PORT erase_flash

    pipenv run python -m esptool --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ~/Downloads/esp32-$VERSION.bin

### REPL

    pipenv run mpfshell
    
### Transfer code to device

From the top-level project directory, run the `transfer.py` helper script, replacing `$APP` with the desired code directory:

    pipenv run python transfer.py ./deivce/$APP/

### Output

    screen /dev/ttyUSB0 115200

To exit: `ctl-a d`
