"""
Manages EQU tokens
"""
from icecream import ic
from ..core import constants
from ..core import Expression, EquateSymbolError
from ..tokens import Tokenizer, TokenGroup, TokenType

# TOK = const.TOK
# DIR = const.DIR
# LBL = const.LBL
# EQU = const.EQU

# #############################################################################


class Equate:
    """Represent an EQU statement."""
    __slots__ = ('label', 'expression', 'token_group')
    label: str | None
    expression: Expression | None
    token_group: TokenGroup | None

    def __init__(self, tokens: TokenGroup):
        """Create an Equate object instance given an initial dictionary."""
        if len(tokens) < 3:
            raise EquateSymbolError(f"Incomplete {constants.EQU} definition.")
        self.token_group = self.equ_tokens(tokens)
        if self.token_group is None:
            raise EquateSymbolError(f"Missing {constants.EQU} definition")
        self.label = self.token_group.element_at(0).value
        self.expression = self.token_group.element_at(2).data

    def __str__(self):
        """Return a string representatio n of this Equate object."""
        if self.label:
            desc = f"{self.label} = {hex(self.expression)}\n"
            return desc
        return None

    def __repr__(self):
        """Return a string respresendation of how the object was created."""
        desc = f"Equate({self.token_group})"
        return desc

    @classmethod
    def from_string(cls, line: str) -> "Equate":
        """Create a new Equate object from a string."""
        if line and constants.EQU in line.upper():
            group = Tokenizer().tokenize_string(line)
            return Equate(group)
        return cls({})

    def equ_tokens(self, tokens: TokenGroup) -> TokenGroup | None:
        """Return just the tokens that make up the EQU.

        Normally, the entire group is just the EQU but in the event that there
        are more tokens before and/or after the EQU statement, this function
        will isolate them and return a new group."""
        idx = tokens.find_first_value(constants.EQU)
        if idx and idx > 0:
            new_group = TokenGroup()
            new_group.add(tokens.element_at(idx-1))
            new_group.add(tokens.element_at(idx))
            new_group.add(tokens.element_at(idx+1))
            return new_group
        return None

    # --------========[ End of class ]========-------- #
