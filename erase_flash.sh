PORT=$(ls /dev/tty.usbserial-* | head -n1)
pipenv run python -m esptool --port $PORT erase_flash
# pipenv run python -m esptool --port $PORT --chip esp8266 --before no_reset --after no_reset erase_flash
