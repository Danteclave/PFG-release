from unittest import TestCase
from rng.mersenne_rng import MersenneRng


class TestMersenneRng(TestCase):

    def test_init(self):
        rng, rng2 = MersenneRng(), MersenneRng()
        states = (rng.random.getstate(), rng2.random.getstate())

        self.assertIsInstance(rng, MersenneRng)
        self.assertIsInstance(rng2, MersenneRng)
        self.assertNotEqual(*states)

    def test_next(self):
        rng = MersenneRng(seed=42)
        self.assertIsInstance(rng, MersenneRng)
        self.assertEqual(83810, rng.random.randint(0, 99999))
        pass
