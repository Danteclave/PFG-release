import struct

from rng import ScramRng
from schema.pfgschema import PFGSchema

from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

pfg = PFGSchema(100, 100)
if __name__ == "__main__":
    with open("pfg.bin", "wb") as f:
        for i in range(1024 * 1024 * 100):
            outnums = [pfg.next() for _ in range(8)]

            byte = 0
            for num in outnums:
                byte = (byte << 1) | num

            f.write(byte.to_bytes(1, byteorder="little"))
