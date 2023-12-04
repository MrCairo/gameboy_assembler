"""Hold a set of lexeme tokens."""

from __future__ import annotations
from typing import Optional
from collections import OrderedDict

from ..core.constants import DIR_T, ARGS_T, REMN_T, BAD_T, TYPE_T, \
    DIRECTIVES, INST, SYM
from ..cpu.instruction_set import InstructionSet as IS
from ..core.symbol import SymbolUtils


# A Token represents a set of lexemes that comprise a single line of source
# code.
#
# Example:
#
#   The text: "SECTION 'game_vars', WRAM0[$0100]" would generate tokens like:
#
#   {'directive': 'SECTION',
#    'type': 'ORIGIN',      #  Same as SECTION
#    'arguments': {'arg00': 'SECTION',
#                  'arg01': "'game_vars'",
#                  'arg02': 'WRAM0[$0100]'}}
#
#   {'directive': '.label:',
#    'type': 'SYMBOL'
#    'arguments': {'arg00': '.label:'}}
#
#     - The 'directive' is the actual command, in this case a SECTION
#       directive. The next part of the dictionary is an array of
#       parameters. Parameter 0 is always the directive. The remaining
#       parameters are there to support the directive.


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
        desc = f"Token.from_elements([{str(self)}])"
        return desc

    def __str__(self) -> str:
        """Return a human readable string for this object."""
        desc = f"{self.as_string()}"
        return desc
        # desc = f"DIR = {self.directive}\n"
        # desc += f"TYPE = {self.type_str}\n"
        # desc += f"ARGS = {self.arguments.values()}"
        # if REMN_T in self._tok:
        #     desc += f"REMN = {self.remainder.__str__()}"
        # return desc

    def as_string(self) -> str:
        """Return the token as a string representation of a list."""
        desc = "'" + "', '".join(self._tok[ARGS_T]) + "'"
        if self.remainder is not None:
            tok2 = self.remainder
            desc += ", "+tok2.as_string()
        return desc

    @property
    def type_str(self) -> Optional[str]:
        """Return the type string of this token."""
        return self._tok[TYPE_T]

    @type_str.setter
    def type_str(self, value: str):
        """Set the token type string."""
        self._tok[TYPE_T] = value

    @property
    def directive(self) -> Optional[str]:
        """Property getter to return the DIR_T value."""
        return self._tok[DIR_T] if DIR_T in self._tok else None

    @directive.setter
    def directive(self, value: str):
        """Property setter to set the DIR_T value."""
        self._tok[DIR_T] = value if value is not None else None

    @property
    def arguments(self) -> Optional[list]:
        """Return ARGS for this token."""
        return self._tok[ARGS_T] if ARGS_T in self._tok else None

    @arguments.setter
    def arguments(self, value: list):
        """Set the ARGS for this token."""
        if value is not None:
            args = {f'arg{idx:02d}': x for idx, x in enumerate(value)}
            self._tok[ARGS_T] = args

    @property
    def remainder(self) -> Optional[Token]:
        """Get the REMN, if any, from this token."""
        return self._tok[REMN_T] if REMN_T in self._tok else None

    @remainder.setter
    def remainder(self, value: Token):
        """Set the REMN value for this token."""
        if value is not None:
            self._tok[REMN_T] = value

    @classmethod
    def from_elements(cls, elements: list) -> Token:
        """Initialze the objet and backing store."""
        if elements is None:
            raise ValueError("Missing list of lexemes as input.")
        tok = Token()
        tok.assign(elements)
        return tok

    @classmethod
    def from_components(cls, directive: str, type_str: str, *, args: list,
                        remainder: Optional[Token] = None) -> Token:
        """Create a Token object from values."""
        tok = Token()
        if directive is not None:
            tok.directive = directive
        else:
            raise ValueError("'directive' must have a value")
        tok.type_str = type_str
        if args is not None:
            tok.arguments = args
        if remainder is not None:
            tok.remainder = remainder
        return tok

    def assign(self, pieces: list):
        """Assign list values to the Token."""
        if pieces[0] in DIRECTIVES:
            self.directive = pieces[0]
            self.type_str = DIR_T
            self._tok[ARGS_T] = pieces
        elif IS().is_mnemonic(pieces[0]):
            self.directive = pieces[0]
            self.type_str = INST
            self._tok[ARGS_T] = pieces
        elif SymbolUtils.is_valid_symbol(pieces[0]):
            self.directive = pieces[0]
            self.type_str = SYM
            self._tok[ARGS_T] = pieces[:1]
            # Symbol only has a single value It is possible that more
            # instructions are on the same line as the symbol. In this case,
            # we simply recusively add it to the remainder attribute
            if len(pieces) > 1:
                self.remainder = Token.from_elements(pieces[1:])
        else:
            self.directive = BAD_T
            self._tok[ARGS_T] = pieces

    # --------========[ End of Token class ]========-------- #
