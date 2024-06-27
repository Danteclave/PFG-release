import math
from typing import Tuple


def reduce_frac(val: Tuple[int, int] | int,
                val2: int | None = None) -> Tuple[int, int]:
    numerator, denominator = val, val2
    if isinstance(val, Tuple):
        if val2 is not None:
            raise ValueError(f"Incompatible types: {type(val)}, {type(val2)}")
        numerator, denominator = val
    if isinstance(val, int):
        if not isinstance(val2, int):
            raise ValueError(f"Incompatible types: {type(val)}, {type(val2)}")

    gcd = math.gcd(numerator, denominator)

    return numerator // gcd, denominator // gcd


def lcg(seed: int) -> int:
    m = int(2**32)
    a = 1664525
    c = 1013904223
    seed = (a * seed + c) % m
    return seed
