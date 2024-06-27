from typing import Tuple

from rng.abstract_rng import AbstractRng
from rng.mersenne_rng import MersenneRng
from schema.smoothing import Smoother, NoneSmoother
from utils.utils import reduce_frac


class PFGSchema:

    def next(self) -> bool:
        val = self.inner_generator.next(self.get_pq())
        if val:
            self.reg_win()
        else:
            self.reg_loss()
        return val

    def __init__(self,
                 wins: int,
                 losses: int,
                 inner_generator: type(AbstractRng) = MersenneRng,
                 smoother: type(Smoother) = NoneSmoother):

        self.current_wins = wins
        self.current_losses = losses
        self.wins = wins
        self.losses = losses

        self.smoother = smoother()

        self.inner_generator = inner_generator() if isinstance(MersenneRng, inner_generator) else inner_generator(self)
        self.update(wins, losses)

    def __repr__(self):
        return ("PFGSchema("
                f"{self.wins},"
                f"{self.losses},"
                f"{self.current_wins},"
                f"{self.current_losses},"
                f"{self.inner_generator}"
                f"{self.smoother}"
                f")")

    def __eq__(self, o):
        return (isinstance(o, PFGSchema) and self.wins == o.wins
                and self.losses == o.losses
                and self.current_wins == o.current_wins
                and self.current_losses == o.current_losses
                and self.inner_generator == o.inner_generator
                and self.smoother == o.smoother)

    def get_pq(self) -> Tuple[int, int]:  # wins/losses
        return self.current_wins, self.current_losses

    def _reg(self, what=True):
        if what:
            self.current_wins -= 1
        else:
            self.current_losses -= 1
        self.refresh()

    def reg_win(self):
        self._reg(what=True)

    def reg_loss(self):
        self._reg(what=False)

    def refresh(self):
        if self.current_wins + self.current_losses == 0:
            self.wins, self.losses = reduce_frac(self.wins, self.losses)
            self.current_wins = self.wins
            self.current_losses = self.losses

    def update(self, wins: int, losses: int):
        if self.current_wins != 0 and self.current_losses != 0:
            self.current_wins, self.current_losses = self.smoother.get_new_pq(
                (self.current_wins, self.current_losses), (wins, losses))
        self.wins = wins
        self.losses = losses
        self.inner_generator.make_seed()
