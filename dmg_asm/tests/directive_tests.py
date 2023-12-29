"""DMG Assembler unit tests."""

# import os
import unittest
from icecream import ic
from ..directives import Equate
from ..core import Convert


class DirectiveUnitTests(unittest.TestCase):
    """Directive Unit Tests."""

    def test_equate_from_string(self):
        """Test Equate class."""
        equ = Equate.from_string("VAR_NAME EQU $0100")
        self.assertTrue(equ is not None)
        self.assertTrue(equ.label == "VAR_NAME")
        self.assertEqual(Convert(equ.expression).to_decimal_int(),
                         256, "Expression not euqal to 256.")

        ic(equ)
        #  End of unit tests
