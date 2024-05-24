# -*- mode: python; fill-column: 79;     -*-
"""Assemble a GameBoy Z80 program into binary."""


# from io import open, TextIOWrapper
# from dataclasses import dataclass

from ..core.constants import Environment
from ..core.label import Label, Labels
from ..core.symbol import Symbol, Symbols
from ..core.exception import DefineAssignmentError, DefineException, \
    DefineSymbolError, SectionException, InvalidSymbolName, \
    InvalidSymbolScope, ExpressionException
from ..tokens import Token, TokenGroup, TokenType
from ..directives import Define, Section, Sections, Mnemonic, \
    Storage
from ..cpu.instruction_pointer import InstructionPointer
from .application_store import Application

INCL_PREFIX = "INCLUDE "


class AssemblerUtils:
    """Assemble GameBoy Z80 source files into a binary file."""

    def __init__(self, env: Environment):
        """Initialize the assembler with an environment."""
        if env is None or not isinstance(env, Environment):
            msg = "'env' must be a valid Environment object."
            raise TypeError(msg)
        self._env = env

    def process_tokens(self, token_group: TokenGroup) -> bool:
        """Assemble a GB Z80 source file into binary.

        Anything that resolves into something that would either result into
        code or alter the IP is then stored into the Application() singleton.
        Anything else, like a label or a symbol is stored in their respective
        storages.

        The first element of the token group is processed. During processing,
        all elements that are needed are consumed and the NEXT token is then
        returned. This allows for things like a Symbol and a directive or
        instruction to be written on a single line.

        This function is then called recusrively until all token elements have
        been processed.
        """
        group_len = len(token_group)
        if token_group is None or group_len == 0:
            return False
        first = token_group[0]
        grp = None
        match first.type:
            case TokenType.DIRECTIVE:
                grp = self.resolve_any_primary_directive(token_group)
            case TokenType.STORAGE_DIRECTIVE:
                grp = self.resolve_any_storage(token_group)
            case TokenType.INSTRUCTION:
                grp = self.resolve_any_instruction(token_group)
            case TokenType.SYMBOL:
                grp = self.resolve_any_symbol(token_group)
            case _:
                grp = token_group[1:] if group_len > 1 else TokenGroup()
        if len(grp):
            new_grp = TokenGroup.from_token_list(grp)
            return self.process_tokens(new_grp)
        return True

    # -----[ Top-level processors ]-----------------------------------

    def resolve_any_primary_directive(self,
                                      token_group: TokenGroup) -> TokenGroup:
        """Process any token group starting with a DIRECTIVE."""
        first = token_group[0].value.upper()
        match first:
            case "DEF":
                tok = self._process_define(token_group)
            case "SECTION":
                tok = self._process_section(token_group)
        if tok is not None:
            last_idx = token_group.index_of(tok)
            return token_group[last_idx:]
        return TokenGroup()

    def resolve_any_storage(self, token_group: TokenGroup) -> TokenGroup:
        """Process an storage type directive."""
        if len(token_group) > 1:
            stor = Storage(token_group)
            if stor is not None:
                Application().append_code(stor.bytes())
                return TokenGroup()
        return token_group[1:]

    def resolve_any_instruction(self, token_group: TokenGroup) -> TokenGroup:
        """Process any gbz80 instruction."""
        if len(token_group) > 1:
            try:
                mnemonic = Mnemonic(token_group)
            except ExpressionException as err:
                raise ExpressionException from err
            Application().append_code(mnemonic.instruction_detail.code)
        return TokenGroup()

    def resolve_any_symbol(self, token_group: TokenGroup) -> TokenGroup | None:
        """Process any Symbol."""
        tok = self._process_symbol(token_group)
        idx = token_group.index_of(tok)
        if idx is not None and idx + 1 < len(token_group):
            return token_group[idx + 1:]
        return TokenGroup()

    # -----[ Individual processors ]----------------------------------

    #
    # DEF label EQU value
    #
    def _process_define(self, token_group: TokenGroup) -> Token:
        try:
            define: Label = Define(token_group)
        except (DefineSymbolError,
                DefineAssignmentError, DefineException) as err:
            print(err)
            return False
        Labels().push(define)  # A DEF is a subclass of a Label
        return token_group[4] if len(token_group) > 4 else None

    #
    # SECTION "name", BLOCK[offset], BANK[num], ALIGN[align]
    #
    def _process_section(self, token_group: TokenGroup) -> Token | None:
        """Process a SECTION from a TokenGroup. Return the last Token
        processed or None if there was an error."""
        try:
            sec = Section(token_group)
        except (TypeError, SectionException) as err:
            print(err)
            return None
        Sections().push(sec)
        Application().create_new_address_entry(sec.starting_address)
        idx = sec.parser_info.last_idx + 1
        if idx < len(token_group):
            last_tok = token_group[idx]
            return last_tok
        return None

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
