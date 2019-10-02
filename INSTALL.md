# Install

Note: All instructions for Windows are guess-work only:

## Python 3

### Ubuntu

    sudo apt-get install -y python3 python3-pip

### Windows

Download and run the installer:

https://www.python.org/downloads/release/python-374/

## PIP3

Check if version 3 is already installed:

    pip3 --version

or:

    pip --version

If not installed:

### Ubuntu

    sudo apt-get install -y python3-pip

### Windows

    (not sure)

## Pipenv

    pip3 install pipenv

(or just `pip` depending)

## Project Code

If git is installed:

    git clone https://github.com/reillybeacom/micropython-home-assistant-iot.git

Otherwise download zip:

https://github.com/reillybeacom/micropython-home-assistant-iot/archive/master.zip

Unzip and change to the directory:

    cd micropython-home-assistant-iot

## Install Python Packages

    pipenv install

## Download Micropython

Latest version from here:

https://micropython.org/download#esp8266

eg:

https://micropython.org/resources/firmware/esp8266-20190529-v1.11.bin

Save it to the `bin` directory (folder).

## Pre-test any electronics wiring

Before connecting to a PC, power up the device using a cheap USB wall-adaptor and USB cable.

If anything starts smoking or getting hot, disconnect the power and do not continue with this guide as it might also fry your PC's USB port.

(Further, if this is the first attempt at connecting to the ESP8266, remove all shields and wiring and only connect the main board itself. This will limit the number of possible causes of unknown errors.)

## Connect ESP8266 via USB

Plug in ESP8266 via USB and find the port...

### Linux

    ls -l /dev/ttyUSB*

### Windows

Go into device manager and confirm what port your device is on:

https://cdn.instructables.com/F08/LFZ6/IXGFN0MB/F08LFZ6IXGFN0MB.LARGE.jpg?auto=webp&frame=1&width=914&fit=bounds

## Install MicroPython to ESP8266 device

Replace `${PORT}` with either `/dev/ttyUSB?` or `COM?`

### Erase the memory

    pipenv run python -m esptool --port ${PORT} erase_flash

### Install new firmware

Replace `${PORT}` and `${BINFILE}`

    pipenv run python -m esptool --port ${PORT} --baud 115200 write_flash 0 bin/${BINFILE}

### Set WiFi and MQTT details:

Create a file called `secrets.py`

Add the following code, filling in the blanks:

```
WIFI_NAME=""
WIFI_PASSWORD=""

MQTT_SERVER=""
MQTT_USER=""
MQTT_PASSWORD=""
MQTT_PORT=1883
```

### Build and transfer project code to the ESP8266 device

    pipenv run python transfer.py device/solar_hot_water_controller

You should now see a REPL connected to the ESP8266. Try typing `1+1` to confirm everything is working.

### Reset the device

There is a small button on the side of the ESP8266 board. Press it. Debug logs should start to appear in the REPL.
