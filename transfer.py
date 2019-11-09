from argparse import ArgumentParser
from shutil import copyfile
import mpy_cross
import os, sys, subprocess, datetime, glob
from platform import system

parser = ArgumentParser()
parser.add_argument("-c", "--clean", action="store_true", help="Remove build files.")
parser.add_argument("-m", "--modified-only", action="store_true", help="Only transfer modified files.")
parser.add_argument("-b", "--build-only", action="store_true", help="Build only without calling mpfshell.")
parser.add_argument("source", action="store", type=str, help="Directory containing micropython main.py file and other device code.")
args = parser.parse_args()

lib_dir = os.path.abspath(os.path.join(".", "lib"))
source_dir = os.path.abspath(args.source)
build_dir = os.path.join(source_dir, "_build")
build_lib_dir = os.path.join(build_dir, "lib")

if not os.path.isdir(lib_dir):
    raise FileNotFoundError(lib_dir)

if not os.path.isdir(source_dir):
    raise FileNotFoundError(source_dir)

if system() == "Windows":
    port = "COM1" ## TODO: How to detect active ports on Windows?
else:
    port = list(set(os.listdir("/dev")).intersection(['tty.usbserial-144310', 'tty.usbserial-1420', 'ttyUSB0', 'ttyUSB1']))[0]

def pathfix(path):
    if system() == "Windows":
        return path.replace("c:\\", "/").replace("C:\\", "/").replace("\\", "/")
    else:
        return path

commands = [
    "open %s" % port,
    "lcd %s" % pathfix(build_dir.replace(os.path.abspath("."), ".")),
]

try:
    os.mkdir(build_dir)
    os.mkdir(build_lib_dir)
except FileExistsError:
    pass

# copyfile(os.path.join(lib_dir, 'boot.py'), os.path.join(build_dir, 'boot.py'))

# commands.append("put ./boot.py")

with open(os.path.join(build_dir, 'main.py'), 'w') as f:
    f.write("import _main")

commands.append("put ./main.py")

for source_file in glob.iglob(os.path.join(source_dir, "**", "*.py"), recursive=True):
    if build_dir not in source_file:
        print(source_file)
        source_file_dir, source_file_name = os.path.split(source_file)
        if source_file_name == 'main.py':
            source_file_name = '_main.py'
        target_dir = source_file_dir.replace(source_dir, build_dir)
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, source_file_name.replace('.py', '.mpy'))
        print(' --> ' + target_file)
        if not os.path.isfile(target_file) or not args.modified_only or  os.path.getmtime(source_file) > os.path.getmtime(target_file):
            mpy_cross.run("-o", target_file, source_file)
            mk_dirs = []
            for sub_dir in target_dir.replace(build_dir, "").split('/'):
                if len(sub_dir) > 0:
                    mk_dirs.append(sub_dir)
                    command = "md %s" % pathfix(os.path.join(*mk_dirs))
                    if command not in commands:
                        commands.append(command)
            commands.append("put %s" % pathfix(target_file.replace(build_dir, ".")))

print('---------------------------------------------------------------')
    
with open(os.path.join(source_dir, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() != '' and line[0] != "#"]
    
with open(os.path.join(lib_dir, 'version.py'), 'w') as f:
    f.write("build_date = '{:%Y/%m/%d}'".format(datetime.datetime.today()))

requirements.append('version.py')

for requirement in requirements:
    requirement_file = os.path.join(lib_dir, requirement)
    print(requirement_file)
    if not os.path.isfile(requirement_file):
        raise FileNotFoundError(requirement_file)
    requirement_dir, requirement_file_name = os.path.split(requirement)
    target_dir = os.path.join(build_lib_dir, requirement_dir)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, requirement_file_name.replace('.py', '.mpy'))
    print(' --> ' + target_file)
    if not os.path.isfile(target_file) or not args.modified_only or os.path.getmtime(requirement_file) > os.path.getmtime(target_file):
        mpy_cross.run("-o", target_file, requirement_file)
        mk_dirs = []
        for sub_dir in target_dir.replace(build_dir, "").split('/'):
            if len(sub_dir) > 0:
                mk_dirs.append(sub_dir)
                command = "md %s" % pathfix(os.path.join(*mk_dirs))
                if command not in commands:
                    commands.append(command)
        commands.append("put %s" % pathfix(target_file.replace(build_dir, ".")))
    
print('---------------------------------------------------------------')

commands.append("ls")
commands.append("repl")

for c in commands:
    print(c)
    
print('---------------------------------------------------------------')

joiner = "; " if system() == "Windows" else "\\; "
command = "mpfshell -c %s" % joiner.join(commands)

print(command)

if args.build_only:
    print('Dry run.')
else:
    subprocess.call(command, shell=True)
