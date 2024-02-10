"""DMG Assembler unit tests."""

# import os
import unittest

from ..tokens.tokenizer import Tokenizer
from ..core.reader import BufferReader
from ..core.label import Labels, Label
from ..core.symbol import Symbol, Symbols
from ..core.expression import Expression
from ..directives.mnemonic import Mnemonic

ASM_1 = """
USER_IO    EQU $FF00

ld hl, USER_IO
"""


class InstructionDecodingTests(unittest.TestCase):
    """Token Unit Tests."""

    labels: Labels

    def setUp(self):
        self.labels = Labels()
        self.labels.clear()

    def tearDown(self):
        self.labels.clear()

    def test_ld_reg_reg(self):
        """Tokenize and decode several LD r, r instructions."""
        line = "ld b, c"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertTrue(inst.instruction_detail.addr == Expression('$41'))

        line = "ld c, (hl)"
        inst = Mnemonic(Tokenizer().tokenize_string(line))
        self.assertTrue(inst.instruction_detail.addr == Expression('078'))

        line = "ld (hl), H"
        inst = Mnemonic(Tokenizer().tokenize_string(line))
        self.assertTrue(inst.instruction_detail.addr == Expression('$74'))

    def test_ld_with_label(self):
        """Tokenize and decode an LD with reference to a Label."""
        Labels().push(Label("USER_IO", Expression("$BEEF")))
        line = "ld hl, USER_IO"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$21"))

    def test_ldh(self):
        """Test the LDH variation of instruction."""
        # Basic
        line = "ldh ($20), A"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$E0"))

        line = "ldh A, ($32)"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$F0"))

    def test_ldh_with_label(self):
        """Test eval of a label."""
        Labels().push(Label("HIGH", Expression("$CB")))
        Labels().push(Label("LOW", Expression("$41")))
        # with label
        line = "ldh (HIGH), A"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$E0"))
        self.assertTrue(inst.instruction_detail.operand1.upper() == "($CB)")

        line = "ldh A, (LOW)"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$F0"))
        self.assertTrue(inst.instruction_detail.operand2 == "($41)")

    def test_jr_cond_relative(self):
        """Test JR with different registers."""
        line = "JR NZ, $41"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$20"))

    def test_ld_hl_sp(self):
        """Test the parsing of the unique LD HL, SP+r8."""
        line = "LD HL, SP+$41"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$f8"))

    def test_ld_hl_sp_with_label(self):
        """Test the parsing of the unique LD HL, SP+r8."""
        Labels().push(Label("OFFSET", Expression("$7f")))
        line = "LD HL, SP+OFFSET"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$f8"))

    def test_jp_absolute(self):
        """Test the JP a16 instruction."""
        line = "JP $0100"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$c3"))

    def test_js_absolute_with_symbol(self):
        """Test the JP a16 with a Symbol."""
        symbol = Symbol("prog_main:", Expression("$0200"))
        Symbols().add(symbol)
        line = "JP prog_main:"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$c3"))
        self.assertTrue(inst.instruction_detail.operand1 == "$0200")

    def test_halt(self):
        """Test the HALT instruction."""
        line = "HALT"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$76"))

    def test_redo_if_symbol_changes(self):
        """Test the resolve_again feature of the Mnemonic instance."""
        symbol = Symbol("prog_main:", Expression("$0200"))
        Symbols().add(symbol)
        line = "JP prog_main:"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$c3"))
        self.assertTrue(inst.instruction_detail.operand1 == "$0200")
        symbol.base_address = Expression("$ffd2")
        inst.resolve_again()
        self.assertTrue(inst.instruction_detail.addr == Expression("$c3"))
        self.assertTrue(inst.instruction_detail.operand1 == "$FFD2")

    def test_redo_if_label_changes(self):
        """Test the resolve_again feature of the Mnemonic instance."""
        Labels().push(Label("HIGH", Expression("$CB")))
        Labels().push(Label("LOW", Expression("$41")))
        line = "ldh (HIGH), a"
        tokens = Tokenizer().tokenize_string(line)
        inst = Mnemonic(tokens)
        self.assertIsNotNone(inst)
        self.assertIsNotNone(inst.instruction_detail)
        self.assertTrue(inst.instruction_detail.addr == Expression("$e0"))
        self.assertTrue(inst.instruction_detail.operand1 == "($CB)")
        # Update Label's value
        Labels().push(Label("HIGH", Expression("%00010001")), replace=True)
        # re-do mnemonic so that the new Label is resolved again
        inst.resolve_again()
        self.assertTrue(inst.instruction_detail.addr == Expression("$e0"))
        self.assertTrue(inst.instruction_detail.operand1 == "($11)")

    def tokenize_lines(self):
        """Test tokenization of a small set of program lines."""
        _reader = BufferReader(ASM_1)
        _line = ''
        while _reader.is_eof() is False:
            _line = _reader.read_line()
            if _line and len(_line) > 0:
                groups = Tokenizer().tokenize_string(_line)
                if len(groups) == 0:
                    continue

    #  End of unit tests
