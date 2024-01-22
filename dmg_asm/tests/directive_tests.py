"""DMG Assembler unit tests."""

# import os
import unittest

# pylint: disable=relative-beyond-top-level
from ..core import Convert
from ..core.expression import Expression
from ..directives import Equate, Define
from ..directives.section import Section
from ..tokens import TokenGroup, Tokenizer


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

    def test_section_from_string(self):
        """Test the SECTION Directive supplied as a string."""
        section = 'SECTION "CoolStuff", WRAM0, BANK[2]'
        group = Tokenizer().tokenize_string(section)
        self.assertTrue(len(group) > 0)

    def test_section_find_label_and_mem_block(self):
        """Find first label and enclosing delmiters."""
        code = 'SECTION "coolstuff", WRAM0[$4567]'
        group: TokenGroup = Tokenizer().tokenize_string(code)
        self.assertTrue(group is not None)
        sec: Section = Section(group)
        self.assertIsNotNone(sec.label)
        self.assertTrue(sec.label.lower() == "coolstuff")
        self.assertIsNotNone(sec.memory_block)
        self.assertTrue(sec.memory_block.name == "WRAM0")
        self.assertIsNotNone(sec.memory_block_offset)
        test_expr = Expression("$4567")
        self.assertTrue(sec.memory_block_offset == test_expr)


#  End of unit tests
