"""DMG Assembler unit tests."""

# import os
import unittest
from icecream import ic

from ..tokens.token import Token
from ..tokens.token_group import TokenGroup
from ..tokens.tokenizer import Tokenizer
from ..core.constants import SYM, TokenType
from ..core.reader import BufferReader
from ..lex import lexer_parser, lexer_results, lexical_analyzer, lexical_node

ASM_1 = """
;; Program

USER_IO    EQU $FF00
SECTION "CoolStuff",WRAM0
CLOUDS_X: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,\\
             $00,$FF,$00
BUILDINGS_X: DS 1
FLOOR_X: DS 1
PARALLAX_DELAY_TIMER: DS 1
FADE_IN_ACTIVE:: DS 1
FADE_STEP: DS 1
ALLOW_PARALLAX:: DS 1
READ_INPUT:: DS 1
START_PLAY:: DS 1

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


class TokenUnitTests(unittest.TestCase):
    """Token Unit Tests."""

    def test_token_group_from_string(self):
        """Tokenize elements from a string."""
        group = Tokenizer().tokenize_string('SECTION "CoolStuff", WRAM0')
        self.assertTrue(group is not None)
        tok = group[0]
        self.assertTrue(tok.value == "SECTION")
        self.assertTrue(len(group) == 5)
        self.assertTrue(group[4].value == "WRAM0")
        self.assertTrue(tok.type == TokenType.DIRECTIVE)
        self.assertTrue(group[2].type == TokenType.LITERAL)
        self.print_group(group)

    def test_token_group_from_elements(self):
        """Test Tokenize an array of instructions and data."""
        line = "CLOUDS_Y: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00," \
            "$FF,$00,$FF,$00,$FF,$00"
        group = Tokenizer().tokenize_string(line)
        self.print_group(group)
        self.assertTrue(group is not None)
        self.assertTrue(len(group) == 18)
        self.assertTrue(group[0].type == TokenType.SYMBOL)

    def test_tokenize_instruction(self):
        """Tokenize a line of CPU instruction."""
        inst = "jr nz, .update_game"
        group = Tokenizer().tokenize_string(inst)
        self.assertTrue(group is not None)
        self.assertTrue(group[0].type == TokenType.KEYWORD)

    def test_tokenize_lines(self):
        """Test tokenization of a small set of program lines."""
        _reader = BufferReader(ASM_1)
        _line = ''
        while _reader.is_eof() is False:
            _line = _reader.read_line()
            # chunks = lexer_parser.tokenize_line(_line)
            # ic(chunks)
            if _line and len(_line) > 0:
                ic("")
                ic("***** BEGIN Parse Line *****")
                ic(_line)
                groups = Tokenizer().tokenize_string(_line)
                if len(groups) == 0:
                    ic("line ignored")
                    continue
                self.print_group(groups)
                ic("***** END Parse Line *****")
                ic("")
            else:
                ic("line ignored.")

    def print_group(self, group):
        ic("--------------------------------------")
        ic("Token Group(s):")
        index = 0
        for token in group.tokens():
            grouping = f"{index:02d}: {str(token)}"
            ic(grouping)
            index += 1
        ic("--------------------------------------")

        #  End of unit tests


if __name__ == "__main__":
    unittest.main()
