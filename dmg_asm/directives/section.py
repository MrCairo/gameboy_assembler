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
from ..core.expression import Expression as Expr, ExpressionException
from ..tokens import TokenGroup, Tokenizer, TokenType
from ..core.exception import SectionDeclarationError
from ..core.constants import QUOTE_PUNCTUATORS, DELIMITER_PAIRS, \
    DPair, DelimData

# ##############################################################################
# SecAddress is a Tuple that holds a start and end


class AddrRange(NamedTuple):
    """Tuple that represents an address range for a memory bank.

    start is an Expression representing the beginning of the address range.
    end is an Expression representing the end of the address range.
    """
    start: Expr
    end: Expr


class MemoryBlock(NamedTuple):
    """Represents a memory block consisting of a start and end address."""
    id: int
    range: AddrRange


@dataclass
class SectionMemBlock:
    """Represent a named memory bank with associated AddressRange.

    Optionally, an numeric ID can be added to further help identify the bank.
    """

    __slots__ = ('name', 'id', 'range')
    name: str
    range: AddrRange
    id: int | None

    def __init__(self, name: str, addr_range: AddrRange,
                 identifier: int = -1):
        self.name = name
        self.range = addr_range
        self.id = identifier


# ##############################################################################


class SectionType:
    """
    A class of address types from WRAM0 to OAM.
    These names are used to easily
    reference special address blocks of the Game Boy system.
    """

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(SectionType, cls).__new__(cls)
            # ------------------------------------------------------------
            # These are the memory banks
            cls.instance._mem_blocks = [
                # Working Ram
                SectionMemBlock(name="WRAM0",
                                addr_range=AddrRange(start=Expr("0xC000"),
                                                     end=Expr("0xCFFF"))),

                # Video Ram
                SectionMemBlock(name="VRAM",
                                addr_range=AddrRange(start=Expr("0x8000"),
                                                     end=Expr("0x9FFF"))),

                # Progam switching area for ROM banks
                # This will point to ROM banks 0x01-0x7F
                SectionMemBlock(name="ROMX",
                                addr_range=AddrRange(start=Expr("0x4000"),
                                                     end=Expr("0x7FFF"))),

                # RPM Bank 0
                SectionMemBlock(name="ROM0",
                                addr_range=AddrRange(start=Expr("0x0000"),
                                                     end=Expr("0x3FFF"))),

                # CPU Work RAM or Stack RAM
                SectionMemBlock(name="HRAM",
                                addr_range=AddrRange(start=Expr("0xFF80"),
                                                     end=Expr("0xFFFE"))),

                # Switchable working RAM for banks 1-7
                SectionMemBlock(name="WRAMX",
                                addr_range=AddrRange(start=Expr("0xD000"),
                                                     end=Expr("0xDFFF"))),

                # External Expansion Working RAM
                SectionMemBlock(name="SRAM",
                                addr_range=AddrRange(start=Expr("0xA000"),
                                                     end=Expr("0xBFFF"))),

                # OAM (40 display data OBJs) (40 x 32 bits)
                # Object Attribute Memory
                SectionMemBlock(name="OAM",
                                addr_range=AddrRange(start=Expr("0xFE00"),
                                                     end=Expr("0xFE9F")))
            ]
            cls.instance._mem_options = [
                # Bank selector
                SectionMemBlock(name="BANK",
                                addr_range=AddrRange(start=Expr("0x0000"),
                                                     end=Expr("0x0007"))),

                # Bank address alignment
                SectionMemBlock(name="ALIGN",
                                addr_range=AddrRange(start=Expr("0x0000"),
                                                     end=Expr("0x0080")))

            ]
        return cls.instance
    # @property
    # def mem_banks(self):
    #     """Return a dict of memory blocks that are valid in a SECTION."""
    #     return self._mem_blocks

    def is_valid_sectiontype(self, section_type: str) -> bool:
        """Return True if the sectionType is valid. False otherwise."""
        sec = section_type.upper().strip()
        items = [x for x in self._mem_blocks if x.name is sec]
        return len(items) > 0

    def is_option(self, option_name: str) -> bool:
        """Return True if the option_name is a valid option."""
        option = option_name.upper().strip()
        items = [x for x in self._mem_options if x.name is option]
        return len(items) > 0

    def mem_option_info(self, option_name: str) -> SectionMemBlock | None:
        option = option_name.upper().strip()
        items = [x for x in self._mem_options if x.name is option]
        # Only one should be found.
        return items[0] if len(items) else None

    def sectiontype_info(self, section_type: str) -> SectionMemBlock | None:
        """Return the memory bank info associated with a SectionType name."""
        sec = section_type.upper().strip()
        items = [x for x in self._mem_blocks if x.name == sec]
        # Only one should be found.
        return items[0] if len(items) else None


@dataclass
class SectionData:
    # pylint: disable=too-many-instance-attributes
    section_key: bool = False
    label: str = None
    block_name: str = None
    block_offset: Expr = None
    bank_key: str = None
    bank_num: str = None
    align_key: str = None
    align_val: str = None
    error: bool = False
    idx: int = 0

# #############################################################################


class Section:
    """Represent a SECTION directive including the label and memory bank."""

    __slots__ = ('_tokens', '_data')

    def __init__(self, tokens: TokenGroup | None):
        self._tokens: TokenGroup = tokens
        if tokens is None:
            raise TypeError("Tokens passed to a Section cannot be None.")
        if len(tokens) < 5:
            # [SECTION, \", LABEL, \", BLOCK]
            msg = "Missing one or more parameters."
            raise SectionDeclarationError(msg)
        self._data = _parse(tokens)

    def __repr__(self) -> str:
        desc = f"Section({self._tokens.__repr__()})"
        return desc

    def __str__(self) -> str:
        desc = "SECTION "
        desc += f"\"{self.label}\" {self.memory_block.name}"
        if self.memory_block_offset:
            desc += f"[{self.memory_block_offset.clean_str}"
        if self.memory_bank:
            desc += f" BANK[{self.memory_bank}]"
        if self.alignment:
            desc += "f ALIGN[{self.alignment}]"
        desc += "\n"
        return desc

    @classmethod
    def section_from_string(cls, text: str) -> Section:
        """Creates a new Section given it's command in a text string."""
        group = Tokenizer().tokenize_string(text)
        return Section(group)

    @property
    def label(self) -> str | None:
        """Return the Section's Label string."""
        return self._data.label if self._data else None

    @property
    def memory_block(self) -> SectionMemBlock | None:
        """Return the memory block of the Section."""
        block = None
        if self._data and self._data.block_name:
            block = SectionType().sectiontype_info(self._data.block_name)
        return block

    @property
    def memory_block_offset(self) -> Expr | None:
        """Return the memory block offset as an expression or None if the
        expression was invalid or missing.
        """
        expr = None
        if self._data and self._data.block_offset:
            try:
                expr = Expr(self._data.block_offset)
            except ExpressionException:
                return None
        return expr

    @property
    def memory_bank(self) -> int | None:
        """Return the memory BANK value as an int if one was specified."""
        if self._data and self._data.bank_num:
            return int(self._data.bank_num)
        return None

    @property
    def alignment(self) -> int | None:
        """Return the ALIGN value as an int if one was specified."""
        if self._data and self._data.align_val:
            return int(self._data.align_val)
        return None


# ============================================================


def _parse(tokens: TokenGroup) -> SectionData:
    data = SectionData()
    data.idx = 0
    dir_idx: int = 0

    curr_directive: str = None
    for idx, tok in enumerate(tokens):
        if idx < dir_idx:
            continue
        match tok.type:
            case TokenType.DIRECTIVE:
                if tok.value == "SECTION":
                    data.section_key = "SECTION"
                    curr_directive = tok.value
                    dir_idx = idx + 1
            case TokenType.BEGIN_PUNCTUATOR | TokenType.PUNCTUATOR:
                enclosure = _get_enclosed_value(tokens,
                                                dir_idx)
                if enclosure.label:
                    match curr_directive:
                        case "SECTION":
                            data.label = enclosure.label
                        case "MEMORY_DIRECTIVE":
                            data.block_offset = enclosure.label
                        case "BANK":
                            data.bank_num = enclosure.label
                        case "ALIGN":
                            data.align_val = enclosure.label
                        case _:
                            data.error = True
                    dir_idx = enclosure.end + 1
            case TokenType.MEMORY_DIRECTIVE:
                if data.label:  # Must have label before mem block
                    data.block_name = tok.value
                    dir_idx = idx + 1
                    curr_directive = "MEMORY_DIRECTIVE"
                else:
                    data.error = True
                    break
            case TokenType.MEMORY_OPTION:
                if data.block_name:  # No option before memory block
                    if tok.value == "BANK":
                        data.bank_key = tok.value
                        dir_idx = idx + 1
                    elif tok.value == "ALIGN":
                        data.align_key = tok.value
                        dir_idx = idx + 1
                    else:
                        break  # Unknown memory option
                    curr_directive = tok.value
                else:
                    break
        if data.error:
            break
    return data


def _get_enclosed_value(tokens: TokenGroup,
                        start_idx: int = 0) -> DelimData:
    """Return delimiter enclosure data.

    This function will seek for the first delimiter found beginning at
    'start_idx' and continue to parse until an ending delimiter is found.

    If there is no ending delimiter found before the end of the token group or
    if the found delimiters are not a recognized delimiter pairing, then
    this function will return a 'DelimData' with the 'd_pair' element set to
    None and the label, even if found, is set to None. It's important to note
    that 'label' is always a string (which is why it's not called 'value').

    Note: A delimiter pair is like { }. An invalid pairing would be [ }
          Nested delimiters are not supported.
    """
    start: int = None
    end: int = None
    label: str = None
    pair: DPair = None
    if start_idx < 0 or start_idx > len(tokens):
        return None
    for idx, tok in enumerate(tokens):
        if idx < start_idx:
            continue
        match tok.type:
            case TokenType.BEGIN_PUNCTUATOR:
                start = idx
                continue
            case TokenType.LITERAL:
                label = tok.value
                continue
            case TokenType.EXPRESSION:
                if start:
                    label = tok.value
                    continue
                break
            case TokenType.END_PUNCTUATOR:
                end = idx
                break
            case TokenType.PUNCTUATOR:
                if tok.value not in QUOTE_PUNCTUATORS:
                    continue
                if not start:
                    start = idx
                    continue
                if not end and start:
                    end = idx
                    break
    if start and end:
        d1 = tokens[start].value  # Opening delimiter
        d2 = tokens[end].value    # Closing delimiter
        pair: DPair = [x for x in DELIMITER_PAIRS
                       if x[0] == d1 and x[1] == d2]
        # If the found delimiters are not a correct pair, forget the label
        label = None if not pair else label
    return DelimData(start, end, pair, label)
