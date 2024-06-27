import math
from abc import ABC, abstractmethod
from typing import Tuple, cast

from utils.utils import reduce_frac


class Smoother(ABC):

    @abstractmethod
    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        pass


class NoneSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        return new_pq


class AverageSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        return [(old_pq[i] + new_pq[i]) // 2 for i in range(2)]


class BiasedLinearSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        old_pq, new_pq = reduce_frac(old_pq), reduce_frac(new_pq)
        return (4 * old_pq[0] + new_pq[0]) // 5, (4 * old_pq[1] +
                                                  new_pq[1]) // 5


class KeepPreviousSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        return old_pq


class NonLinearSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        k = -math.exp(-0.2 * (old_pq[0] / (old_pq[0] + old_pq[1]))**2 -
                      (new_pq[0] / (new_pq[0] + old_pq[1]))**2)
        return math.floor(k * old_pq[0] + new_pq[0]), math.ceil(k * old_pq[1] +
                                                                new_pq[1])


class AddReduceSmoother(Smoother):

    def get_new_pq(self, old_pq: Tuple[int, int], new_pq: Tuple[int, int]):
        old_pq, new_pq = reduce_frac(old_pq), reduce_frac(new_pq)
        return reduce_frac(
            cast(Tuple[int, int],
                 tuple(old_pq[i] + new_pq[i] for i in range(2))))
