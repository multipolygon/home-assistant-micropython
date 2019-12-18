from argparse import ArgumentParser
from shutil import copyfile
import mpy_cross
import os, sys, subprocess, datetime, glob
from platform import system

parser = ArgumentParser()
parser.add_argument("--clean", "-c", action="store_true", help="Remove build files.")
parser.add_argument("--modified-only", "-m", action="store_true", help="Only transfer modified files.")
parser.add_argument("--build-only", "-b", action="store_true", help="Build only without calling mpfshell.")
parser.add_argument("--cross-compile", "-x", action="store_true", help="Cross-compile (compress) to Micropython byte code.")
parser.add_argument("source", action="store", type=str, help="Directory containing micropython main.py file and other device code.")
args = parser.parse_args()

base_dir = os.path.abspath(".")
lib_dir = os.path.join(base_dir, "lib")
source_dir_name = os.path.split(args.source.strip(os.path.sep))[-1]
source_dir = os.path.join(base_dir, "src", source_dir_name)
build_dir = os.path.join(base_dir, "build", "mpy" if args.cross_compile else "py", source_dir_name)

if not os.path.isdir(lib_dir):
    raise FileNotFoundError(lib_dir)

if not os.path.isdir(source_dir):
    raise FileNotFoundError(source_dir)

if args.build_only:
    port = None
elif system() == "Windows":
    port = "COM1" ## TODO: How to detect active ports on Windows?
else:
    port = os.path.split(list(glob.iglob("/dev/tty.usbserial-*"))[0])[-1]

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
except FileExistsError:
    pass

copyfile(os.path.join(lib_dir, 'secrets.py'), os.path.join(build_dir, 'secrets.py'))
commands.append("put ./secrets.py")

copyfile(os.path.join(lib_dir, 'boot.py'), os.path.join(build_dir, 'boot.py'))
commands.append("put ./boot.py")

def build(source_dir, source_file):
    if not os.path.isfile(source_file):
        raise FileNotFoundError(source_file)
    print(source_file)
    source_file_dir, source_file_name = os.path.split(source_file)
    target_dir = source_file_dir.replace(source_dir, build_dir)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, source_file_name)
    if args.cross_compile and not(target_file.endswith('config.py')):
        target_file = target_file.replace('.py', '.mpy')
    print(' --> ' + target_file)
    target_file_relative = pathfix(target_file.replace(build_dir, "."))
    if not os.path.isfile(target_file) or not args.modified_only or os.path.getmtime(source_file) > os.path.getmtime(target_file) or target_file_relative == './main.py' or target_file_relative == './main.mpy':
        if target_file.endswith('.mpy'):
            mpy_cross.run("-o", target_file, source_file)
        else:
            copyfile(source_file, target_file)
        mk_dirs = []
        for sub_dir in target_dir.replace(build_dir, "").split('/'):
            if len(sub_dir) > 0:
                mk_dirs.append(sub_dir)
                command = "md %s" % pathfix(os.path.join(*mk_dirs))
                if command not in commands:
                    commands.append(command)
        command = "put %s" % target_file_relative
        if command not in commands:
            commands.append(command)

for source_file in glob.iglob(os.path.join(source_dir, "**", "*.py"), recursive=True):
    build(source_dir, source_file)

print('---------------------------------------------------------------')

with open(os.path.join(source_dir, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() != '' and line[0] != "#"]
    
with open(os.path.join(lib_dir, 'version.py'), 'w') as f:
    f.write("build_date = '{:%Y/%m/%d}'".format(datetime.datetime.today()))

requirements.append('version.py')

for requirement in requirements:
    requirement_file = os.path.join(lib_dir, requirement)
    build(base_dir, requirement_file)
    
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
