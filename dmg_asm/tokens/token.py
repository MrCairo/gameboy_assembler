"""Hold a set of lexeme tokens."""

from __future__ import annotations
from typing import Optional, Union
from collections import OrderedDict

from ..core.constants import \
    DIRECTIVES, INST, SYM, DIR, BAD, TokenType, MEMORY_BLOCKS, \
    VAL_T as value_t, ARGS_T as arguments_t, NEXT_T as next_t, \
    REMN_T as remainder_t, TYPE_T as type_t
from ..cpu.instruction_set import InstructionSet as IS
from ..core.symbol import SymbolUtils
from ..core.exception import InvalidSymbolName, InvalidSymbolScope

LEXEMES = [
    value_t,
    arguments_t,
    next_t,
    remainder_t,
    type_t
]


# A Token represents a set of lexemes that comprise a single line of source
# code.
#
# Example:
#
#   The text: "SECTION 'game_vars', WRAM0[$0100]" would generate tokens like:
#
#   {'type': 'ORIGIN',
#    'value': 'SECTION',
#    'arguments': ['SYMBOL',
#                  "'game_vars'",
#                  'WRAM0[$0100]']
#
#   {'value': '.label:',
#    'type': 'SYMBOL'
#    'arguments': ['.label:'] }

#   {'value': '.label:',
#    'type': 'SYMBOL'
#    'arguments': ['.label:'] }
#
#     - The 'value' is the actual command, in this case a SECTION of type
#       'ORIGIN'. The next part of the dictionary is an array of parameters
#       which are the arguments to support the value of the token.  Arguments
#       are always present since element 0 of the argument repeats the
#       original value of the token. Parameter 0 is always the value of the
#       toek type followed by the remaining elements. The remaining parameters
#       are there to support the directive.


class Token:
    """Object that encapsulates pieces of parsed data (lexemes).

    This object is an accessor class to the underlying data structure that
    represents a line of source code text. The Token class itself doesn't
    parse, but it is used to store the divided up pieces without resorting to
    an untyped dictionary.
    """

    def __init__(self):
        """Initialize an empty token."""
        self._tok = OrderedDict()

    def __repr__(self) -> str:
        """Return representation on how this object can be built."""
        desc = f"Token.from_elements(['{self.value}'])"
        if self.next:
            desc += f"\n{self.next.__repr__()}"
        return desc

    def __str__(self) -> str:
        """Return a human readable string for this object."""
        desc = f"Value: '{self.value}', Type: {self.type}"
        if self.next:
            desc += f"\n{self.next.__str__()}"
        return desc

    def to_string(self) -> str:
        """Return the token as a string representation of a list."""
        # Since the arguments lexeme also contains the directive asm
        # the first element, we can just use arguments here.
        desc = "'" + "', '".join(self.arguments) + "'"
        if self.remainder is not None:
            tok2 = self.remainder
            desc += ", "+tok2.to_string()
        return desc

    # Helper functions
    @property
    def value(self) -> str:
        """Return the token value as a string, or None if empty."""
        return self.lexeme(value_t)

    @property
    def arguments(self) -> Optional[dict]:
        """Return the directive value as a string, or None if empty."""
        return self.lexeme(arguments_t)

    @property
    def next(self) -> Optional[Token]:
        """Return the directive value as a string, or None if empty."""
        return self.lexeme(next_t)

    @property
    def remainder(self) -> Optional[list]:
        """Return the remaining element(s) that aren't part of the token.

        These remaining elements may result in another token but we don't
        recurse by creating another token here."""
        return self.lexeme(remainder_t)

    @property
    def type(self) -> Optional[str]:
        """Return the directive value as a string, or None if empty."""
        return self.lexeme(type_t)

    #
    # Primary getter and setter for the token.
    #

    def lexeme(self, key: str) -> Optional[str | dict | None]:
        """Return an entry from the Token dict if present."""
        return self._tok.get(key, None)

    def set_lexeme(self, key: str, value: Union[str | dict | Token]) -> bool:
        """Assign a value to a new or existing lexeme in the Token."""
        if key not in LEXEMES:
            return False
        if key == arguments_t:
            args = [x for idx, x in enumerate(value)]
            # args = {f'arg{idx:02d}': x for idx, x in enumerate(value)}
            self._tok[key] = args
        else:
            self._tok[key] = value
        return True

    @classmethod
    def from_elements(cls, elements: list) -> Token:
        """Create a new token from a list of elements."""
        if not elements:
            raise ValueError("List of elements missing.")
        tok = Token()
        tok._assign(elements)
        return tok

    def _assign(self, pieces: list):
        """Assign list values to the Token."""
        if pieces is None or len(pieces) == 0:
            return
        try:
            if pieces[0] in DIRECTIVES:
                self._assign_directive(pieces)
            elif pieces[0] in MEMORY_BLOCKS:
                self._assign_mem_block(pieces)
            elif IS().is_mnemonic(pieces[0]):
                self._assign_instruction(pieces)
            elif SymbolUtils.is_valid_symbol(pieces[0]):
                self._assign_symbol(pieces)
            elif len(pieces[0]) == 1 and pieces[0] in "\"'([{}])":
                self._assign_delimiter(pieces)
            else:
                self._assign_literal(pieces)
        except (InvalidSymbolName, InvalidSymbolScope) as err:
            self._assign_invalid([err] + pieces)

    def _assign_invalid(self, elements):
        self.set_lexeme(type_t, BAD)
        self.set_lexeme(value_t, BAD)
        if len(elements):
            self.set_lexeme(value_t, elements[0])
            self.set_lexeme(arguments_t, elements)

    def _assign_directive(self, elements) -> bool:
        """Assigns the Token's lexems for a directive."""
        if elements is None:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, TokenType.DIRECTIVE)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_mem_block(self, elements) -> bool:
        """Assigns the Token's lexems for a directive."""
        if elements is None:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, TokenType.MEMORY_BLOCK)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_instruction(self, elements) -> bool:
        if elements is None or len(elements) == 0:
            return False
        # ins = IS().instruction_from_mnemonic(elements[0].upper())
        self.set_lexeme(value_t, elements[0].upper())
        self.set_lexeme(type_t, TokenType.KEYWORD)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_symbol(self, elements) -> bool:
        if elements is None or len(elements) == 0:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, TokenType.SYMBOL)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_delimiter(self, elements) -> bool:
        if elements is None or len(elements) == 0:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, TokenType.PUNCTUATOR)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_literal(self, elements) -> bool:
        if elements is None or len(elements) == 0:
            return False
        self.set_lexeme(value_t, elements[0])
        self.set_lexeme(type_t, TokenType.LITERAL)
        if len(elements) > 1:
            self._assign_next(elements[1:])
        return True

    def _assign_next(self, elements) -> bool:
        tok = Token.from_elements(elements)
        self.set_lexeme(next_t, tok)
        return True
        # if elements is None or len(elements) == 0:
        #     return False
        # tok = Token.from_elements(elements)
        # if tok.type is not BAD:
        #     self.set_lexeme(next_t, tok)
        # return True

    def _assign_remainder(self, elements) -> bool:
        if elements is None or len(elements) == 0:
            return False
        self.set_lexeme(remainder_t, elements)
        return True

    # --------========[ End of Token class ]========-------- #
