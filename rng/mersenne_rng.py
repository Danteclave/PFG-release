from random import Random
from typing import Tuple
from rng.abstract_rng import AbstractRng


class MersenneRng(AbstractRng):

    def __init__(self,
                 seed: int | float | str | bytes | bytearray | None = None):
        self.random = Random(seed) if seed else Random()
        pass

    def next(self, pq: Tuple[int, int]) -> bool:
        return self.random.randint(0, sum(pq)) < pq[0]
