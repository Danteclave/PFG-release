from unittest import TestCase
from rng.scram_rng import ScramRng
from schema.pfgschema import PFGSchema


class TestScramRng(TestCase):

    def test_init(self):
        rng, rng2 = [ScramRng(PFGSchema(100, 100)) for i in range(2)]
        states = (rng.seed, rng2.seed)

        self.assertIsInstance(rng, ScramRng)
        self.assertIsInstance(rng2, ScramRng)
        self.assertEqual(*states)

        rng3 = ScramRng(PFGSchema(111, 999))

        self.assertNotEqual(rng.seed, rng3.seed)

    def test_next(self):
        rng = ScramRng(PFGSchema(100, 100))
        self.assertIsInstance(rng, ScramRng)
        self.assertEqual(3098791263, rng._next())
        pass
