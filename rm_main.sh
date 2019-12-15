cd /dev
PORT=$(ls tty.usbserial-* | head -n1)
cd -
pipenv run mpfshell --noninteractive -c "open $PORT; rm main.py; rm main.mpy"
pipenv run mpfshell --noninteractive --reset
