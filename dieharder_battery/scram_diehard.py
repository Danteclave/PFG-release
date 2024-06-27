import struct

from rng import ScramRng
from schema.pfgschema import PFGSchema

from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

scram = ScramRng(PFGSchema(100, 100))

if __name__ == "__main__":
    with open("scram.bin", "wb") as f:
        for i in range(25000000):
            number = scram._next()
            f.write(struct.pack("I", number))
