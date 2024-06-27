from unittest import TestCase
from unittest.mock import patch, MagicMock

from schema.pfgschema import PFGSchema


class TestPFG(TestCase):

    def setUp(self):
        pass

    def testNoneSmoother(self):
        with patch("utils.utils.reduce_frac", MagicMock()) as mock:
            pfg = PFGSchema(1, 99)
            pfg._reg(True)
            pfg._reg(False)

            mock.assert_not_called()
