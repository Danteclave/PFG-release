from typing import Tuple

from rng.abstract_rng import AbstractRng
from schema.pfgschema import PFGSchema
from utils.utils import lcg


# self-contained random number generator
class ScramRng(AbstractRng):

    def __init__(self, pfg_schema: PFGSchema):
        self.schema = pfg_schema

        self.seed: int = 0

        self.make_seed()
        pass

    def make_seed(self):
        c_pq = self.schema.get_pq()
        pq = self.schema.wins, self.schema.losses

        wins, cwins = pq[0], c_pq[0]
        loss, closs = pq[1], c_pq[1]

        avg = cwins / wins + closs / loss
        avg /= 2 / max(1, sum(pq))

        self.seed = int(avg * 10**6) ^ self.seed

        return self.seed

    def _next(self):
        self.seed = lcg(self.seed)
        return self.seed

    def next(self, pq: Tuple[int, int]) -> bool:
        ret = self._next()
        return ret % sum(pq) > pq[0]
