"""DMG Assembler unit tests."""

# import os
import unittest
from icecream import ic
from ..directives import Equate, Define
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

    def test_define_from_string(self):
        """Test Define class."""
        equ = Define.from_string("DEF my_var EQU $1000")
        self.assertTrue(equ is not None)
        self.assertTrue(equ.label.upper() == "MY_VAR")
        self.assertEqual(Convert(equ.expression).to_decimal_int(),
                         4096, "Expression not euqal to 4096.")


#  End of unit tests
