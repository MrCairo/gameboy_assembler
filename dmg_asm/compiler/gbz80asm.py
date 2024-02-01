"""Assemble a GameBoy Z80 program into binary."""

# from io import open, TextIOWrapper
# from dataclasses import dataclass

from ..core.constants import Environment
from ..core.label import Label, Labels
from ..core.symbol import Symbol, Symbols
from ..core.exception import DefineAssignmentError, DefineException, \
    DefineSymbolError, SectionException, InvalidSymbolName, InvalidSymbolScope

from ..tokens import Token, TokenGroup, TokenType
from ..directives import Define, Section, Sections
from ..cpu.instruction_pointer import InstructionPointer

INCL_PREFIX = "INCLUDE "


class Assembler:
    """Assemble GameBoy Z80 source files into a binary file."""

    def __init__(self, env: Environment):
        """Initialize the assembler with an environment."""
        if env is None or not isinstance(env, Environment):
            msg = "'env' must be a valid Environment object."
            raise TypeError(msg)
        self._env = env

    def assemble(self, token_group: TokenGroup) -> bool:
        """Assemble a GB Z80 source file into binary."""
        group_len = len(token_group)
        if token_group is None or group_len == 0:
            return False
        first = token_group[0]
        grp = None
        match first.type:
            case TokenType.DIRECTIVE:
                grp = self.process_any_primary_directive(token_group)
            case TokenType.STORAGE_DIRECTIVE:
                grp = self.process_any_storage(token_group)
            case TokenType.INSTRUCTION:
                grp = self.process_any_instruction(token_group)
            case TokenType.SYMBOL:
                grp = self.process_any_symbol(token_group)
            case _:
                grp = token_group[1:] if group_len > 1 else TokenGroup()
        if len(grp):
            return self.assemble(grp)
        return True

    # -----[ Top-level processors ]-----------------------------------

    def process_any_primary_directive(self,
                                      token_group: TokenGroup) -> TokenGroup:
        """Process any token group starting with a DIRECTIVE."""
        first = token_group[0].value.upper()
        match first:
            case "DEF":
                self._process_define(token_group)
            case "SECTION":
                self._process_section(token_group)
        return token_group[1:] if len(token_group) > 1 else TokenGroup()
        # Check for EQU or EQUS
        # second = token_group[1].value.upper()
        # match second:
        #     case "EQU":
        #         return self._process_equate(token_group)
        #     case "EQUS":
        #         return self._process_equate(token_group)
        # return False

    def process_any_storage(self, token_group: TokenGroup) -> TokenGroup:
        """Process an storage type directive."""
        if len(token_group) > 1:
            return token_group[1:]
        return TokenGroup()

    def process_any_instruction(self, token_group: TokenGroup) -> bool:
        """Process any gbz80 instruction."""
        if len(token_group) > 1:
            return token_group[1:]
        return TokenGroup()

    def process_any_symbol(self, token_group: TokenGroup) -> TokenGroup | None:
        """Process any Symbol."""
        tok = self._process_symbol(token_group)
        idx = token_group.index_of(tok)
        if idx and idx + 1 < len(token_group):
            return token_group[idx + 1:]
        return TokenGroup()

    # -----[ Individual processors ]----------------------------------

    def _process_define(self, token_group: TokenGroup) -> Token:
        try:
            define: Label = Define(token_group)
        except (DefineSymbolError,
                DefineAssignmentError, DefineException) as err:
            print(err)
            return False
        Labels().push(define)  # A DEF is a subclass of a Label
        return token_group[3]

    def _process_section(self, token_group: TokenGroup) -> Token | None:
        """Process a SECTION from a TokenGroup. Return the last Token
        processed or None if there was an error."""
        try:
            sec = Section(token_group)
        except (TypeError, SectionException) as err:
            print(err)
            return None
        Sections().push(sec)
        idx = sec.parser_info.last_idx
        return token_group[idx]

    def _process_equate(self, token_group: TokenGroup) -> Token | None:
        """Process an EQU from a TokenGroup. Return the last Token
        processed or None if there was an error."""
        return token_group[0]

    def _process_label(self, token_group: TokenGroup) -> Token | None:
        """Process a Label from a TokenGroup. Return the last Token
        processed or None if there was an error."""
        return token_group[0]

    def _process_symbol(self, token_group: TokenGroup) -> Token | None:
        """Process a symbol from a TokenGroup. Return the last Token
        processed or None if there was an error."""
        token = token_group[0]
        if token.data:
            symbol: Symbol = token.data
            symbol.base_address = InstructionPointer().curr_pos()
        else:
            try:
                symbol: Symbol = Symbol(token.value,
                                        InstructionPointer.curr_pos())
            except (InvalidSymbolName, InvalidSymbolScope) as err:
                print(err)
                return None
        Symbols().remove(symbol)
        Symbols().add(symbol)
        return token
