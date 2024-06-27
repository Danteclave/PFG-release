from unittest import TestCase
from schema.smoothing import *


class TestScramRng(TestCase):

    def setUp(self):
        self.old_pq = (123, 456)
        self.new_pq = (888, 999)
        self.pq_combos = (self.old_pq, self.new_pq)

    def testNoneSmoother(self):
        self.assertEqual(self.new_pq,
                         NoneSmoother().get_new_pq(*self.pq_combos))

    def testAverageSmoother(self):
        res = [(self.old_pq[i] + self.new_pq[i]) // 2 for i in range(2)]
        self.assertEqual(res, AverageSmoother().get_new_pq(*self.pq_combos))

    def testBiasedinearSmoother(self):
        res = [reduce_frac(self.old_pq), reduce_frac(self.new_pq)]

        expected_p = 4 * res[0][0] + res[1][0]
        expected_p //= 5

        expected_q = 4 * res[0][1] + res[1][1]
        expected_q //= 5

        self.assertEqual((
            expected_p,
            expected_q,
        ),
                         BiasedLinearSmoother().get_new_pq(*self.pq_combos))

    def testKeepPreviousSmoother(self):
        self.assertEqual(self.old_pq,
                         KeepPreviousSmoother().get_new_pq(*self.pq_combos))
        pass

    def testNonLinearSmoother(self):
        k = -math.exp(-0.2 * (self.old_pq[0] /
                              (self.old_pq[0] + self.old_pq[1]))**2 -
                      (self.new_pq[0] / (self.new_pq[0] + self.old_pq[1]))**2)
        expected = math.floor(k * self.old_pq[0] +
                              self.new_pq[0]), math.ceil(k * self.old_pq[1] +
                                                         self.new_pq[1])
        self.assertEqual(expected,
                         NonLinearSmoother().get_new_pq(*self.pq_combos))

    def testAddReduceSmoother(self):
        res = list((reduce_frac(self.old_pq), reduce_frac(self.new_pq)))

        exp_p = res[0][0] + res[1][0]
        exp_q = res[0][1] + res[1][1]

        expected = reduce_frac(exp_p, exp_q)

        self.assertEqual(expected,
                         AddReduceSmoother().get_new_pq(*self.pq_combos))
