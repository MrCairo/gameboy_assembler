"""DMG Assembler unit tests."""

# import os
import unittest

from icecream import ic

from ..tokens import TokenType, Tokenizer
from ..core.reader import BufferReader
from ..core import Expression
from ..directives import Mnemonic

ASM_1 = """
;; Program

USER_IO    EQU $FF00
DEF USER_ID = $FFD2
SECTION "CoolStuff",WRAM0
CLOUDS_X: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,\\
             $00,$FF,$00
BUILDINGS_X: DS 1
FLOOR_X: DS 1
PARALLAX_DELAY_TIMER: DS $01
FADE_IN_ACTIVE:: DS %00000001
FADE_STEP: DS 0x01
ALLOW_PARALLAX:: DS 001
READ_INPUT:: DS &01
START_PLAY:: DS 001

    ; Read P14
    ld HL, USER_IO
    ld A, $20
    ld [HL], A
    ld A, [HL]
    ld HL, IO_P14
    ld B, [HL]
    ld [HL], A
    ld HL, IO_P14_OLD
    ld [HL], B

"""

ASM_2 = """
USER_IO    EQU $FF00

ld hl, USER_IO
"""


class TokenUnitTests(unittest.TestCase):
    """Token Unit Tests."""

    def test_token_group_from_string(self):
        """Tokenize elements from a string."""
        group = Tokenizer().tokenize_string('SECTION "CoolStuff", WRAM0')
        self.assertTrue(group is not None)
        self.assertTrue(len(group) == 5)
        self.assertTrue(group[0].value == "SECTION")
        self.assertTrue(group[0].type == TokenType.DIRECTIVE)
        self.assertTrue(group[2].type == TokenType.LITERAL)
        self.assertTrue(group[4].value == "WRAM0")
        self.assertTrue(group[4].type == TokenType.MEMORY_DIRECTIVE)

    def test_token_group_from_elements(self):
        """Test Tokenize an array of instructions and data."""
        line = "CLOUDS_Y: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00, \
        $FF,$00,$FF,$00,$FF,$00"
        # print_line(line)
        group = Tokenizer().tokenize_string(line)
        self.assertTrue(group is not None)
        self.assertTrue(len(group) == 18)
        self.assertTrue(group[0].type == TokenType.SYMBOL)

    def test_tokenize_storage(self) -> None:
        """Tokenize a DB storage directive."""
        line = "DB $00, $01, $01, $02, $03, $05, $08, $0d, 021, %00100010"
        group = Tokenizer().tokenize_string(line)
        self.assertIsNotNone(group)

    def test_token_equ(self):
        """Test Tokenize an array of instructions and data."""
        line = "DEF PORT EQU 0xffd2"
        # print_line(line)
        group = Tokenizer().tokenize_string(line)
        self.assertTrue(group is not None)
        # print_group(group)

    def test_tokenize_instruction(self):
        """Tokenize a line of CPU instruction."""
        inst = "jr nz, .update_game"
        # print_line(inst)
        group = Tokenizer().tokenize_string(inst)
        self.assertTrue(group is not None)
        self.assertTrue(group[0].type == TokenType.INSTRUCTION)

        inst = "LD (HL), $ff"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)
        self.assertTrue(detail.operand2.upper() == "$FF")

    def test_instruction_with_expression(self):
        """Create instruction detail from code that includes an expression."""
        inst = "LD (HL), $ff"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)
        self.assertTrue(detail.operand2.upper() == "$FF")

    def test_one_word_instruction(self):
        """Create instruction detail from an instruction like 'NOP'"""
        inst = "HALT"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)

    def test_expressionless_instruction(self):
        """Return detail from an instruction that doesn't require an
        expression."""
        inst = "ADD A, (HL)"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        self.assertTrue(mnemonic.opcode.upper() == "ADD")

    def test_instruction_detail(self):
        """Test instruction detail for an instruction that doesn't require
        an external expression."""
        inst = "ADD A, (HL)"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        self.assertTrue(mnemonic.opcode.upper() == "ADD")
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)
        self.assertTrue(detail.length == 1)
        self.assertTrue(detail.addr == Expression("$86"))

    def test_instruction_detail_with_expression(self):
        """Test instruction detail for an instruction that requires
        an external expression."""
        inst = "LD (HL), $ff"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        self.assertTrue(mnemonic.opcode.upper() == "LD")
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)
        self.assertTrue(detail.length == 2)
        self.assertTrue(detail.addr == Expression("$36"))
        self.assertTrue(detail.operand2.upper() == "$FF")

    def test_instruction_with_register(self):
        """Return detail from an instruction that doesn't require an
        expression."""
        inst = "ADD SP, 0x10"
        # print_line(inst)
        tokens = Tokenizer().tokenize_string(inst)
        self.assertIsNotNone(tokens)
        mnemonic = Mnemonic(tokens)
        self.assertIsNotNone(mnemonic)
        detail = mnemonic.instruction_detail
        self.assertIsNotNone(detail)
        self.assertTrue(Expression(detail.operand2) == Expression("016"))
        self.assertTrue(detail.addr == Expression("$e8"))

    def test_tokenize_lines(self) -> None:
        """Test tokenization of a small set of program lines."""
        _reader = BufferReader(ASM_1)
        _line = ''
        while _reader.is_eof() is False:
            _line = _reader.read_line()
            if _line and len(_line) > 0:
                # print_line(_line)
                groups = Tokenizer().tokenize_string(_line)
                # print_group(groups)
                if len(groups) == 0:
                    continue
    #  End of unit tests


def print_group(group):
    """Print the token group."""
    ic("--------------------------------------")
    ic("Token Group(s):")
    index = 0
    for token in group.tokens():
        grouping = f"{index:02d}: {str(token)}"
        ic(grouping)
        index += 1
    ic("--------------------------------------")


def print_line(line_str):
    """Print the line to parse."""
    ic("++++++++++++++++++++++++++++++++++++++")
    ic("Code to parse:")
    ic(line_str)
    ic("++++++++++++++++++++++++++++++++++++++")
