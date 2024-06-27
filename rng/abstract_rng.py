from abc import abstractmethod
from typing import Tuple


class AbstractRng:

    def __init(self, *args, **kwargs):
        pass

    @abstractmethod
    def next(self, pq: Tuple[int, int]) -> bool:
        pass

    def make_seed(self):
        pass
