"""
Manages DEF tokens
"""
from __future__ import annotations
from ..core import constants, Expression
from ..core import DefineSymbolError, DefineAssignmentError, Label
from ..tokens import Tokenizer, TokenGroup, TokenType

# TOK = const.TOK
# DIR = const.DIR
# LBL = const.LBL
# EQU = const.EQU

# #############################################################################


class Define(Label):
    """Represent a DEF statement used to associate a label to an expression.

    DEF labelname EQU/=/EQUS expression.
    The underlying class of this is the Label class that stores the label name
    and expression. This class also maintains a pointer to the token group as
    well as the assignment text used ('EQU' or '=').

    The 'name' value must begin with a letter and only contain letters,
    numbers or an underscore '_'.
    """

    __slots__ = ('_assignment', '_token_group')
    _assignment: str | None
    _token_group: TokenGroup | None

    def __init__(self, tokens: TokenGroup):
        """Create a 'Define' object instance given an initial dictionary.

        Define(token_group: TokenGroup).
        """
        group: TokenGroup = Define._validate(tokens)
        name: str = group[1].value
        value: Expression = group[3].data
        assignment = group[2].value
        super().__init__(name, value)
        self._token_group = group
        self._assignment = assignment

    def __str__(self):
        """Return a string representatio n of this DEFine object."""
        desc = f"DEF {self.name} "
        desc += f"{self._assignment} {hex(self.value)}\n"
        return desc

    def __repr__(self):
        """Return a string respresendation of how the object was created."""
        desc = f"Define({self._token_group})"
        return desc

    @classmethod
    def _validate(cls, tokens: TokenGroup) -> TokenGroup:
        if len(tokens) < 4:
            raise DefineSymbolError(f"Incomplete {constants.DEF} definition.")
        group: TokenGroup = cls.def_tokens(tokens)
        if group is None:
            raise DefineSymbolError(f"Missing {constants.DEF} definition")
        if group[2].value not in ["EQU", "EQUS", "="]:
            raise DefineAssignmentError("Invalid DEF assignment operator.")
        return group

    @classmethod
    def from_string(cls, line: str) -> Define:
        """Create a new DEFine object from a string."""
        if line and line.upper().startswith("DEF"):
            group = Tokenizer().tokenize_string(line)
            return Define(group)
        return cls({})

    @classmethod
    def def_tokens(cls, tokens: TokenGroup) -> TokenGroup | None:
        """Return just the tokens that make up the DEFine."""
        if len(tokens) >= 4 and \
           tokens[0].type == TokenType.DIRECTIVE and \
           tokens[0].value == "DEF":
            new_group = TokenGroup()
            for idx in range(4):
                new_group.add(tokens[idx])
            return new_group
        return None

    # --------========[ End of class ]========-------- #
