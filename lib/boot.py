# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()
import micropython
micropython.alloc_emergency_exception_buf(100)

if "main.py" not in uos.listdir():
    print("import main")
    import main # main.mpy
