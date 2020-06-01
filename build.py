from argparse import ArgumentParser
from platform import system
from shutil import copy2 as copyfile
from shutil import copystat, move
from tempfile import NamedTemporaryFile
from time import sleep
from urllib.request import urlretrieve
import ast
import mpy_cross
import os, sys, subprocess, datetime, glob

def args():
    p = ArgumentParser()
    
    p.add_argument("source", action="store", type=str, help="Directory containing micropython main.py file.")
    
    b = p.add_argument_group('build')
    b.add_argument("--build", "-b", action="store_true", help="Build only without calling mpfshell.")
    b.add_argument("--fetch", '-f', action="store_true", help="Download vendor libs found in requirements.txt")
    b.add_argument("--cross-compile", "-x", action="store_true", help="Cross-compile (compress) to Micropython byte code.")
    b.add_argument("--clean", '-d', action="store_true", help="Remove build files.")
    
    t = p.add_argument_group('transfer')
    t.add_argument("--transfer", "-t", action="store_true", help="Use mpfshell to copy files to device.")
    t.add_argument("--modified-only", "-m", action="store_true", help="Only transfer modified files.")
    t.add_argument("--port", '-p', action="store", type=str, help='Device port')
    t.add_argument("--repl", '-r', action="store_true", help="REPL.")

    c = p.add_argument_group('config')
    c.add_argument("--config", '-c', action="store", type=str, help='Copy specified file to device as config.py')
    c.add_argument("--secrets", '-s', action="store", type=str, help='Transfer specified file as secrets.json')
    c.add_argument("--uid", '-i', action="store", type=str, help='Device unique id for MQTT saved as uid.py')
    
    return p.parse_args()

args = args()

try:
    port = args.port or os.path.split(list(glob.iglob("/dev/tty.usbserial-*"))[0])[-1]
except:
    port = ""
    
base_dir = os.path.abspath(".")
lib_dir = os.path.join(base_dir, "lib")
source_dir = os.path.abspath(args.source)
main_file = os.path.join(source_dir, 'main.py')
_build_dir_name = os.path.split(source_dir)[1]
build_dir = os.path.join(base_dir, "build", "py", _build_dir_name)
x_build_dir = os.path.join(base_dir, "build", "mpy", _build_dir_name)

if not os.path.isdir(lib_dir):
    raise FileNotFoundError(lib_dir)

if not os.path.isdir(source_dir):
    raise FileNotFoundError(source_dir)

if not os.path.isfile(main_file):
    raise FileNotFoundError(main_file)

with open(os.path.join(lib_dir, 'version.py'), 'w') as f:
    f.write("build_date = '{:%Y/%m/%d}'\n".format(datetime.datetime.today()))

def trash(dir):
    if os.path.isdir(dir):
        dir_path, dir_name = os.path.split(dir)
        trash_dir = os.path.join(dir_path, '_trash', dir_name)
        print('Trash: ' + trash_dir)
        os.makedirs(trash_dir, exist_ok=True)
        move(dir, os.path.join(trash_dir, '{:%Y.%m.%d-%H.%M.%S}'.format(datetime.datetime.now())))

REQUIREMENTS_FILE = 'requirements.txt'
        
def fetch_requirements():
    requirements_file = os.path.join(source_dir, REQUIREMENTS_FILE)
    if not os.path.isfile(requirements_file):
        raise FileNotFoundError(requirements_file)
    with open(requirements_file) as f:
        for target_file, url in (line.strip().split('=',1) for line in f.readlines() if line.strip() != '' and line[0] != "#"):
            target_path = os.path.join(lib_dir, 'vendor', target_file)
            print(url)
            print(' --> ' + os.path.relpath(target_path))
            urlretrieve(url, target_path)
    
def _copy_file(source_file, target_file, depth=1):
    print(('-' * depth * 2) + '> ' + target_file)
    target_dir, target_name = os.path.split(target_file)
    os.makedirs(target_dir, exist_ok=True)
    copyfile(source_file, target_file)

def _module_source(module_name):
    for d, t in ((source_dir, '.'), (lib_dir, './lib')):
        f = os.path.join(d, *module_name.split('.')) + '.py'
        if os.path.isfile(f):
            return f, os.path.abspath(os.path.join(build_dir, t, '.' + f.replace(d, '')))
    return None, None

def _copy_module(module_name, depth=1):
    source_file, target_file = _module_source(module_name)
    if source_file:
        _copy_file(source_file, target_file, depth)
        _copy_dependencies(source_file, depth+1)

def _copy_dependencies(source_file, depth=1):
    modules = set()
    with open(source_file) as f:
        for node in ast.walk(ast.parse(f.read(), filename=source_file)):
            if isinstance(node, ast.ImportFrom):
                modules.add(node.module)
            elif isinstance(node, ast.Import):
                modules.add(node.names[0].name)
    for m in modules:
        _copy_module(m, depth)

def build():
    _copy_file(main_file, main_file.replace(source_dir, build_dir))
    _copy_dependencies(main_file, 2)

def cross_compile():
    files = []
    for build_file in glob.iglob(os.path.join(build_dir, "**", "*.py"), recursive=True):
        if os.path.isfile(build_file):
            target_file = build_file.replace(build_dir, x_build_dir).replace('.py', '.mpy')
            target_dir = os.path.split(target_file)[0]
            os.makedirs(target_dir, exist_ok=True)
            print(target_file)
            mpy_cross.run("-o", target_file, build_file)
            files.append((build_file, target_file))
    sleep(0.1)
    for build_file, target_file in files:
        copystat(build_file, target_file)
    copyfile(os.path.join(lib_dir, 'boot.py'), os.path.join(x_build_dir, 'boot.py'))

def _mpfshell(commands, noninteractive="--noninteractive"):
    subprocess.call("mpfshell %s -c %s" % (noninteractive, "\\; ".join(["open %s" % port] + commands)), shell=True)

TIMESTAMP_FILE = '_timestamp.txt'
TIMESTAMP_FILE_REMOTE = '_timestamp.remote.txt'
    
def _get_timestamp():
    if args.modified_only:
        commands = [
            "get %s %s" % (TIMESTAMP_FILE, TIMESTAMP_FILE_REMOTE),
        ]
        if os.path.isfile(TIMESTAMP_FILE_REMOTE):
            os.remove(TIMESTAMP_FILE_REMOTE)
        _mpfshell(commands)
        if os.path.isfile(TIMESTAMP_FILE_REMOTE):
            with open(TIMESTAMP_FILE_REMOTE) as f:
                return float(f.read())
    return 0

def transfer():
    dir = x_build_dir if args.cross_compile else build_dir
    timestamp = _get_timestamp()
    commands = []
    commands.append("lcd %s" % os.path.relpath(dir))
    newest = 0
    for build_file in glob.iglob(os.path.join(dir, "**", "*"), recursive=True):
        if os.path.isfile(build_file) and os.path.split(build_file)[1] != TIMESTAMP_FILE:
            mtime = os.path.getmtime(build_file)
            if mtime > newest:
                newest = mtime
            if not(args.modified_only) or mtime > timestamp:
                build_file = build_file.replace(dir, "")
                target_dir, target_file = os.path.split(build_file)
                dir_path = ""
                for sub_dir in target_dir.split('/'):
                    if sub_dir:
                        dir_path = os.path.join(dir_path, sub_dir)
                        cmd = "md %s" % dir_path
                        if cmd not in commands:
                            commands.append(cmd)
                commands.append("put .%s" % build_file)
    if not(args.modified_only) or newest > timestamp:
        with open(os.path.join(dir, TIMESTAMP_FILE), 'w') as f:
            f.write(str(newest))
        commands.append("put %s" % TIMESTAMP_FILE)
    commands.append("ls")
    for c in commands:
        print(c)
    _mpfshell(commands)

def config():
    _mpfshell([
        "put %s config.py" % os.path.relpath(args.config),
    ])

def secrets():
    _mpfshell([
        "put %s secrets.json" % os.path.relpath(args.secrets),
    ])
    
def uid():
    f = NamedTemporaryFile('w', suffix=".py", delete=False)
    f.write('UID = "%s"' % args.uid)
    f.close()
    _mpfshell([
        "put %s uid.py" % f.name,
    ])
    os.unlink(f.name)

def repl():
    _mpfshell(['repl'], noninteractive="")
    
if args.clean:
    trash(build_dir)
    trash(x_build_dir)

if args.fetch:
    fetch_requirements()
    
if args.build:
    build()

if args.cross_compile:
    cross_compile()
    
if args.transfer:
    transfer()

if args.config:
    config()
    
if args.secrets:
    secrets()

if args.uid:
    uid()
    
if args.repl:
    repl()
