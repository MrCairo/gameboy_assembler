"""DMG Assembler unit tests."""

# import os
import unittest

from ..tokens.token import Token
from ..tokens.token_group import TokenGroup
from ..tokens.tokenizer import Tokenizer
from ..core.constants import SYM
from ..core.reader import BufferReader

asm1 = """
SECTION "CoolStuff",WRAM0
CLOUDS_X: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00
BUILDINGS_X: DS 1
FLOOR_X: DS 1
PARALLAX_DELAY_TIMER: DS 1
FADE_IN_ACTIVE:: DS 1
FADE_STEP: DS 1
ALLOW_PARALLAX:: DS 1
READ_INPUT:: DS 1
START_PLAY:: DS 1
"""


class TokenUnitTests(unittest.TestCase):
    """Token Unit Tests."""

    def test_token_group_from_string(self):
        """Tokenize elements from a string."""
        group = Tokenizer().tokenize_string('SECTION "CoolStuff", WRAM0')
        tok = group.first()
        print(tok)
        self.assertTrue(tok.value == "SECTION")

    def test_token_group_from_elements(self):
        """Test Tokenize an array of instructions and data."""
        elements = ['CLOUDS_Y:', 'DB',
                    '$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,'
                    '$00,$FF,$00']
#        token = Token.from_elements(elements)
#        print(token)
        # group = Tokenizer().tokenize_elements(elements)
        # token = group.element_at(0)
        # self.assertTrue(group is not None)
        # self.assertTrue(token is not None)
        # self.assertTrue(token.value == "CLOUDS_Y:")

    def test_token_from_elements(self):
        """Test new token from elements."""
        elements = ['CLOUDS_Y:', 'DB',
                    '$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,'
                    '$00,$FF,$00']
        # tok = Token.from_elements(elements)
        # self.assertTrue(tok.type == SYM)

    def test_tokenize_instruction(self):
        """Tokenize a line of CPU instruction."""
        inst = "jr nz, .update_game"
        group = Tokenizer().tokenize_string(inst)
        print(group.first())
        self.assertTrue(group is not None)

    def test_tokenize_lines(self):
        """Test tokenization of a small set of program lines."""
        # _tokenizer = Tokenizer()
        # _reader = BufferReader(asm1)
        # _line = ''
        # group = _tokenizer.token_group
        # while _reader.is_eof() is False:
        #     _line = _reader.read_line()
        #     if _line and len(_line) > 0:
        #         group = _tokenizer.tokenize_string(_line)
        #         print(group)
        # print(group)
        # #  End of unit tests
