"""
Implementation of a Section
"""
#
# Class that parses and contains information about a section.
# There can only be one section per file.
#
from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple
from ..core.constants import EQU, LBL, INST, STOR
from ..core.expression import Expression as Expr
from ..tokens import TokenGroup, Token, Tokenizer, TokenType
from ..core.exception import SectionException, SectionDeclarationError

# ##############################################################################
# SecAddress is a Tuple that holds a start and end


class AddressRange(NamedTuple):
    """Tuple that represents an address range for a memory bank.

    start is an Expression representing the beginning of the address range.
    end is an Expression representing the end of the address range.
    """
    start: Expr
    end: Expr


class MemoryBlock(NamedTuple):
    """Represents a memory block consisting of a start and end address."""
    id: int
    range: AddressRange


@dataclass
class SectionMemoryBank(dataclass):
    """Represent a named memory bank with associated AddressRange.

    Optionally, an numeric ID can be added to further help identify the bank.
    """

    __slots__ = ('name', 'id', 'range')
    name: str
    id: int | None
    range: AddressRange

    def __init__(self, name: str, id: int = -1, range: AddressRange):
        self.name = name
        self.id = id
        self.range = range


# ##############################################################################


class SectionType:
    """
    A class of address types from WRAM0 to OAM.
    These names are used to easily
    reference special address blocks of the Game Boy system.
    """

    def __init__(self):
        """Initialze the object."""
        # ------------------------------------------------------------
        # These are the memory
        self._mem_banks = {
            SectionMemoryBank(name="WRAM0",
                              range=AddressRange(start=Expr("$C000"),
                                                 end=Expr("$CFFF"))),
            # Working Ram
            SectionMemoryBank(name="WRAM0",
                              range=AddressRange(start=Expr("0xC000"),
                                                 end=Expr("0xCFFF"))),

            # Video Ram
            SectionMemoryBank(name="VRAM",
                              range=AddressRange(start=Expr("0x8000"),
                                                 end=Expr("0x9FFF"))),

            # Progam switching area for ROM banks
            # This will point to ROM banks 0x01-0x7F
            SectionMemoryBank(name="ROMX",
                              range=AddressRange(start=Expr("0x4000"),
                                                 end=Expr("0x7FFF"))),

            # RPM Bank 0
            SectionMemoryBank(name="ROM0",
                              range=AddressRange(start=Expr("0x0000"),
                                                 end=Expr("0x3FFF"))),

            # CPU Work RAM or Stack RAM
            SectionMemoryBank(name="HRAM",
                              range=AddressRange(start=Expr("0xFF80"),
                                                 end=Expr("0xFFFE"))),

            # Switchable working RAM for banks 1-7
            SectionMemoryBank(name="WRAMX",
                              range=AddressRange(start=Expr("0xD000"),
                                                 end=Expr("0xDFFF"))),

            # External Expansion Working RAM
            SectionMemoryBank(name="SRAM",
                              range=AddressRange(start=Expr("0xA000"),
                                                 end=Expr("0xBFFF"))),

            # OAM (40 display data OBJs) (40 x 32 bits)
            # Object Attribute Memory
            SectionMemoryBank(name="OAM",
                              range=AddressRange(start=Expr("0xFE00"),
                                                 end=Expr("0xFE9F"))),

            # Bank selector
            SectionMemoryBank(name="BANK",
                              range=AddressRange(start=Expr("0x0000"),
                                                 end=Expr("0x0007")))
        }

    @ property
    def mem_banks(self):
        """Return a dict of memory blocks that are valid in a SECTION."""
        return self._mem_banks

    def is_valid_sectiontype(self, section_type: str) -> bool:
        """Return True if the sectionType is valid. False otherwise."""
        sec = section_type.upper().strip()
        items = [x for x in self._mem_banks if x.name is sec]
        return len(items) > 0

    def sectiontype_info(self, section_type: str) -> SectionMemoryBank | None:
        """Return the memory bank info associated with a SectionType name."""
        sec = section_type.upper().strip()
        items = [x for x in self._mem_banks if x.name == sec]
        if len(items):
            return items[0]  # Should only be one found.
        return None


# #############################################################################

class Section:
    """Represent a SECTION directive including the label and memory bank."""

    __slots__ = ('_tokens', '_mem_bank', '_label', '_alignment')

    def __init__(self, tokens: TokenGroup | None):
        self._tokens = tokens
        self._mem_bank = None

    @ classmethod
    def section_from_string(cls, text: str) -> Section:
        group = Tokenizer().tokenize_string(text)
        return Section(group)

    @ property
    def mem_bank(self) -> SectionMemoryBank:
        return self._mem_bank


class _SectionParser:
    """Parse the section tokens."""
    __slots__ = ("_directive", "_label")

    def __init__(self, tokens: TokenGroup):
        if tokens[0].type is not TokenType.STORAGE_DIRECTIVE:
            raise SectionDeclarationError
        self._tokens = tokens

    def _is_valid(self) -> bool:
        return True

    def _get_all_options(self) -> bool:
        _len = len(self._tokens)
        index = self._tokens.find_first_value("SECTION")
        if index is None:
            return False
        self._directive = self._tokens[index]

        #
        # "MyLabel" or 'MyLabel'. Not "Mylabel' or MyLabel
        if index + 3 < _len:
            punct = ['"', "'"]
            quote = None
            tok = self._tokens[index + 1]
            quote = tok.value if tok.value in punct else None
            if quote is None:
                return False

            label = self._tokens[index + 2]
            tok = self._tokens[index + 3]
            equote = tok.value if tok.value in punct else None
            if equote is None or equote != quote:
                return False
            self._label = label

        index = index + 1 if index < _len else None
        if index is None:
            return False

        if self._tokens[index] in ['"', "'"]:
            index = index + 1 if index < _len else None

    def _get_directive_name(self) -> str | None:
        """Returns SECTION or None."""
        index = self._tokens.find_first_value("SECTION")
        if index is None:
            return None
        return self._tokens[index].upper()
