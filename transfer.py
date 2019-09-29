import os, sys, subprocess
import mpy_cross

dir = sys.argv[1]

port = list(set(os.listdir("/dev")).intersection(['tty.usbserial-1420', 'ttyUSB0', 'ttyUSB1']))[0]

commands = [
    "open %s" % port,
]

with open(os.path.join(dir, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() != '' and line[0] != "#"]

cd = None    
for i in requirements:
    path = os.path.abspath(os.path.join(dir, i))
    # print(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(i)
    # mpy_cross.run(path)
    dirname, filename = os.path.split(path)
    if cd != dirname:
        cd = dirname
        commands.append("lcd %s" % dirname)
    commands.append("put %s" % filename)

commands.append("ls")
commands.append("repl")

for c in commands:
    print(c)

command = "mpfshell -c %s" % "\; ".join(commands)

# print(command)

subprocess.call(command, shell=True)
