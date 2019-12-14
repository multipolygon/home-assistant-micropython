cd /dev
PORT=$(ls tty.usbserial-* | head -n1)
cd -
pipenv run mpfshell --noninteractive -c "open $PORT; rm main.py"
pipenv run mpfshell --noninteractive --reset
