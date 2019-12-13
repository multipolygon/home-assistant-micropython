cd /dev
PORT=$(ls tty.usbserial-* | head -n1)
cd -
pipenv run mpfshell -c "open $PORT; repl"
