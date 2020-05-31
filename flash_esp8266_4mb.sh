PORT=$(ls /dev/tty.usbserial-* | head -n1)
pipenv run python -m esptool --port $PORT --baud 115200 write_flash 0 `ls bin/esp8266* | tail -1`
