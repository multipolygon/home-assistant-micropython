from utime import ticks_ms
import struct
import urandom
from machine import unique_id

urandom.seed(struct.unpack('i', unique_id())[0] + ticks_ms())

def randint(bits=8):
    return urandom.getrandbits(bits)
