from utime import ticks_ms
import struct
import urandom
from machine import unique_id

def random_int(bits=8):
    urandom.seed(struct.unpack('i', unique_id())[0] + ticks_ms())
    return urandom.getrandbits(bits)
