"""Token Parsing Classes and constants."""

from enum import Enum, IntEnum, auto
from dataclasses import dataclass
from collections import namedtuple
from .constants import NODE, DIR, EQU, LBL, INST, STOR, SEC, SYM, PARM
from .constants import ORG, DEF, DIRECTIVES, BRACKETS, STORAGE_DIRECTIVES
from .token import Token


class TokenAssignment:
    """Take a token and evaluate it's contents into something usable."""

    def __init__(self, token: Token):
        """Initialize the object."""
        if self._id_and_evaluate_token(token) is False:
            raise ValueError("Input token is bad.")

    def _id_and_evaluate_token(self, token: Token):
        if token is None:
            return False
        if token.directive is BAD:
            return False
        if token.directive in DIRECTIVES:
            if token.directive is SEC:
                self.parse_section(token)
            elif token.directive in STORAGE_DIRECTIVES:
                self.parse_storage(token)
        pass

    def parse_section(self, tokens):
        """Identify the tokens as SECTION.

        SECTION 'Cool Stuff',ROMX[$4567],BANK[3]
        ['SECTION', ''', 'Cool', 'Stuff', ''',
         ',ROMX', '[', '$4567', ']', ',BANK', '[', '3', ']'

        """
        pass

    def parse_instruction(self, tokens):
        """Identify the tokens as INS."""
        pass

    def parse_symbol(self, tokens):
        """Identify the tokens as SYM."""
        pass

    def parse_storage(self, tokens):
        """Identify the tokens as STOR."""
        pass

    def eval_directive(self, token: Token):
        pass

    # --------========[ End of class ]========-------- #
