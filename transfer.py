import os, sys, subprocess, datetime
import mpy_cross

dir = os.path.abspath(sys.argv[1])

port = list(set(os.listdir("/dev")).intersection(['tty.usbserial-1420', 'ttyUSB0', 'ttyUSB1']))[0]

commands = [
    "open %s" % port,
]

with open('version.py', 'w') as f:
    f.write("build_date = '{:%Y/%m/%d}'".format(datetime.datetime.today()))
    
with open(os.path.join(dir, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() != '' and line[0] != "#"]

cd = None    
for i in requirements:
    path = os.path.abspath(os.path.join(dir, i))
    # print(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(i)
    dirname, filename = os.path.split(path)
    if cd != dirname:
        cd = dirname
        commands.append("lcd %s" % dirname)
    if filename == 'main.py':
        commands.append("put %s" % filename)
    else:
        mpy_cross.run(path)
        commands.append("put %s" % filename.replace('.py', '.mpy'))

commands.append("ls")
commands.append("repl")

for c in commands:
    print(c)

command = "mpfshell -c %s" % "\; ".join(commands)

# print(command)

subprocess.call(command, shell=True)
