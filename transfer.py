from argparse import ArgumentParser
from shutil import copyfile
import mpy_cross
import os, sys, subprocess, datetime, glob
from platform import system
import ast

parser = ArgumentParser()
parser.add_argument("--clean", action="store_true", help="Remove build files.")
parser.add_argument("--modified-only", "-m", action="store_true", help="Only transfer modified files.")
parser.add_argument("--build", "-b", action="store_true", help="Build only without calling mpfshell.")
parser.add_argument("--transfer", "-t", action="store_true", help="Use mpfshell to copy files to device.")
parser.add_argument("--cross-compile", "-x", action="store_true", help="Cross-compile (compress) to Micropython byte code.")
parser.add_argument("--config", '-c', action="store", type=str, help='Use specific file in _config.')
parser.add_argument("source", action="store", type=str, help="Src directory containing micropython main.py file.")
args = parser.parse_args()

base_dir = os.path.abspath(".")
lib_dir = os.path.join(base_dir, "lib")
source_dir = os.path.join(base_dir, "src", args.source)
main_file = os.path.join(source_dir, 'main.py')
_build_dir_name = args.source + (("_%s" % args.config) if args.config else "")
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
    if args.config:
        config_file = os.path.join(source_dir, '_config', args.config + '.py')
        _copy_file(config_file, os.path.join(build_dir, 'config.py'))
        _copy_dependencies(config_file, 2)

def cross_compile():
    for build_file in glob.iglob(os.path.join(build_dir, "**", "*"), recursive=True):
        if os.path.isfile(build_file):
            target_file = build_file.replace(build_dir, x_build_dir).replace('.py', '.mpy')
            target_dir, _ = os.path.split(target_file)
            os.makedirs(target_dir, exist_ok=True)
            print(target_file)
            mpy_cross.run("-o", target_file, build_file)
    copyfile(os.path.join(lib_dir, 'boot.py'), os.path.join(x_build_dir, 'boot.py'))

def transfer():
    port = os.path.split(list(glob.iglob("/dev/tty.usbserial-*"))[0])[-1]
    commands = [
        "open %s" % port,
        "lcd %s" % build_dir.replace(os.path.abspath("."), "."),
    ]
    for build_file in glob.iglob(os.path.join(build_dir, "**", "*"), recursive=True):
        if os.path.isfile(build_file):
            build_file = build_file.replace(build_dir, "")
            target_dir, target_file = os.path.split(build_file)
            dir_path = ""
            for sub_dir in target_dir.split('/'):
                if sub_dir:
                    dir_path = os.path.join(dir_path, sub_dir)
                    cmd = "md %s" % dir_path
                    if cmd not in commands:
                        commands.append(cmd)
            commands.append("put .%s" % build_file)
    commands.append("ls")
    commands.append("repl")
    for c in commands:
        print(c)
    subprocess.call("mpfshell -c %s" % "\\; ".join(commands), shell=True)

if args.build:
    build()

if args.cross_compile:
    cross_compile()

if args.transfer:
    transfer()
