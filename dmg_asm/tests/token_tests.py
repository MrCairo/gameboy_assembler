"""DMG Assembler unit tests."""

# import os
import unittest

from ..tokens.token import Token
from ..tokens.token_group import TokenGroup
from ..tokens.tokenizer import Tokenizer
from ..core.constants import SYM


class TokenUnitTests(unittest.TestCase):
    """Token Unit Tests."""

    def test_token_group_from_string(self):
        """Tokenize elements from a string."""
        group = Tokenizer().tokenize_string('SECTION "CoolStuff", WRAM0')
        tok = group.first()
        self.assertTrue(tok.directive == "SECTION")

    def test_token_group_from_elements(self):
        """Test Tokenize an array of instructions and data."""
        elements = ['CLOUDS_Y:', 'DB',
                    '$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,'
                    '$00,$FF,$00']
        group = Tokenizer().tokenize_elements(elements)
        token = group.element_at(0)
        self.assertTrue(group is not None)
        self.assertTrue(token is not None)
        self.assertTrue(token.directive == "CLOUDS_Y:")

    def test_token_from_elements(self):
        """Test new token from elements."""
        elements = ['CLOUDS_Y:', 'DB',
                    '$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,'
                    '$00,$FF,$00']
        tok = Token.from_elements(elements)
        self.assertTrue(tok.type_str == SYM)


#  End of unit tests
