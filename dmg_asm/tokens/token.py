"""Hold a set of lexeme tokens."""

from __future__ import annotations   # Forward references
from enum import StrEnum, auto
from ..core.constants import \
    VAL_T as value_t, NEXT_T as next_t, TYPE_T as type_t, DATA_T as datum_t, \
    DEFINE_OPERATORS, STORAGE_DIRECTIVES, PUNCTUATORS, DIRECTIVES, \
    MEMORY_DIRECTIVES, MEMORY_OPTIONS, BEGIN_PUNCTUATORS, END_PUNCTUATORS
from ..cpu.instruction_set import InstructionSet as IS
from ..core.symbol import SymbolUtils, Symbol
from ..core.exception import InvalidSymbolName, InvalidSymbolScope
from ..core import Expression


class TokenType(StrEnum):
    """Convenient enums for token used during parsing."""

    COMMENT = auto()
    DIRECTIVE = auto()
    STORAGE_DIRECTIVE = auto()
    EXPRESSION = auto()
    IDENTIFIER = auto()
    INVALID = auto()
    INSTRUCTION = auto()
    LITERAL = auto()
    MEMORY_DIRECTIVE = auto()
    MEMORY_OPTION = auto()
    OPERATOR = auto()
    PUNCTUATOR = auto()
    BEGIN_PUNCTUATOR = auto()
    END_PUNCTUATOR = auto()
    SYMBOL = auto()


LEXEMES = [
    datum_t,
    next_t,
    type_t,
    value_t
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

    __slots__ = ('value', 'type', 'data', 'next')

    value: str | dict | Token | Symbol | Expression
    type: str | None
    data: str | dict | Token | Symbol | Expression | None
    next: Token | None

    def __init__(self):
        """Initialize an empty token."""
        self.value = ""
        self.type = self.data = self.next = None

    def __repr__(self) -> str:
        """Return representation on how this object can be built."""
        subs = [self.value]
        _next = self.next
        while _next is not None:
            subs.append(_next.value)
            _next = _next.next
        desc = f"TokenFactory({subs}).token"
        return desc

    def __str__(self) -> str:
        """Return a human readable string for this object."""
        desc = f"type: {self.type}, val: '{self.value}', "
        desc += f"dat: {type(self.data)}"
        if self.next:
            desc += f"\n{self.next.__str__()}"
        return desc

    def __eq__(self, other: Token) -> bool:
        """Return True if other is equal to this token.

        Equality is defined as equal value and equal type.
        """
        return self.value == other.value and self.type == other.type

    # Helper functions
    def shallow_copy(self) -> Token:
        """Return a copy of this token sans next.

        This is preferred over the copy(obj) or deepcopy(obj) functions since
        we only want to copy the value, type, and data. The next value is not
        copied since it will result in a recusive copy which we don't want.
        """
        new_tok = Token()
        new_tok.value = self.value
        new_tok.type = self.type
        new_tok.data = self.data
        return new_tok

# --------========[ End of Token class ]========-------- #


class TokenFactory:
    """Returns a Token object given a list of elements to parse."""

    def __init__(self, elements: list):
        """Initialize the object give a list of elements.

        Parameter:
        -----------
        elements : list  An array (list) of individual values that can be
                         parsed into a token or set of tokens.
        """
        self._tok = Token()
        self.assign(elements)

    @property
    def token(self) -> Token:
        """Return the token."""
        return self._tok

    def assign(self, elements: list):
        """Assign list values to the Token.

        Parameter:
        -----------
        elements : list  An array (list) of individual values that can be
                         parsed into a token or set of tokens.
        """
        if elements is None or len(elements) == 0:
            return
        try:
            first = elements[0]
            if len(first) == 1 and first in PUNCTUATORS:
                self._assign_values(elements, TokenType.PUNCTUATOR)
            elif first in DIRECTIVES:
                self._assign_values(elements, TokenType.DIRECTIVE)
            elif first in MEMORY_DIRECTIVES:
                self._assign_values(elements, TokenType.MEMORY_DIRECTIVE)
            elif first in MEMORY_OPTIONS:
                self._assign_values(elements, TokenType.MEMORY_OPTION)
            elif first in STORAGE_DIRECTIVES:
                self._assign_values(elements, TokenType.STORAGE_DIRECTIVE)
            elif first in DEFINE_OPERATORS:
                self._assign_values(elements, TokenType.OPERATOR)
            elif Expression.has_valid_prefix(first):
                self._assign_values(elements, TokenType.EXPRESSION)
            elif SymbolUtils.is_valid_symbol(first):
                self._assign_values(elements, TokenType.SYMBOL)
            elif IS().is_mnemonic(first):
                self._assign_values(elements, TokenType.INSTRUCTION)
            else:
                self._assign_values(elements, TokenType.LITERAL)
        except (InvalidSymbolName, InvalidSymbolScope) as err:
            self._assign_invalid([err] + elements)

    def _assign_invalid(self, elements):
        self._tok.type = TokenType.INVALID
        self._tok.value = elements

    def _assign_values(self, elements, tok_type: TokenType) -> bool:
        if elements is None:
            return False
        self._tok.value = elements[0]
        self._tok.type = tok_type
        if len(elements) > 1:
            self._assign_next(elements[1:])

        match tok_type:
            case TokenType.INSTRUCTION:
                self._assign_instruction(elements)
            case TokenType.SYMBOL:
                self._assign_symbol(elements[0])
            case TokenType.EXPRESSION:
                self._assign_expression(elements[0])
            case TokenType.PUNCTUATOR:
                # For a more specific punctuator type:
                if elements[0] in BEGIN_PUNCTUATORS:
                    self._tok.type = TokenType.BEGIN_PUNCTUATOR
                elif elements[0] in END_PUNCTUATORS:
                    self._tok.type = TokenType.END_PUNCTUATOR
        return True

    def _assign_instruction(self, elements: list) -> None:
        mnemonic = elements[0]
        ins = IS().instruction_from_mnemonic(mnemonic.upper())
        self._tok.data = ins

    def _assign_symbol(self, name: str) -> None:
        sym = Symbol(name, 0x00)
        self._tok.data = sym

    def _assign_expression(self, expr: str) -> None:
        self._tok.data = Expression(expr)

    def _assign_next(self, elements) -> bool:
        tok = TokenFactory(elements).token  # Token.from_elements(elements)
        self._tok.next = tok
        return True

# --------========[ End of TokenFactory class ]========-------- #
