from utime import ticks_us
import urandom

def randint(max, seed=''):
    urandom.seed(ticks_us() + seed)
    return round(urandom.getrandbits(8) / 255 * max)
