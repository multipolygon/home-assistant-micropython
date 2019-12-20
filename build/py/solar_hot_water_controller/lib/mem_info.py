import gc
import micropython

def mem_info(s=''):
    gc.collect()
    print("Mem: %d%% [%s]" % (round(gc.mem_alloc() / (gc.mem_alloc() + gc.mem_free()) * 100 ), s))
    # print(micropython.mem_info())
