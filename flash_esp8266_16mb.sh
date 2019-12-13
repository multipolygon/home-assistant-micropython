PORT=$(ls /dev/tty.usbserial-* | head -n1)
pipenv run python -m esptool --port $PORT --after no_reset --baud 460800 erase_flash
pipenv run python -m esptool --port $PORT write_flash 0xffc000 bin/esp_init_data_default.bin
pipenv run python -m esptool --port $PORT --baud 460800 write_flash -fm dio -fs 16MB 0x00000 `ls bin/esp8266* | tail -1`
