"""Commonly used constants."""

from dataclasses import dataclass
from collections import namedtuple
from typing import NamedTuple
from enum import auto, Enum, IntEnum

# Token element keys (keys of the token dictionary)
ARGS_T = "arguments"
BAD_T = "unknown"
DATA_T = "data"
DIR_T = "directive"
INST_T = "instruction"
MULT_T = "multiple"
NEXT_T = "next"
NODE_T = "node"  # Rpresents an internal tokenized node.
PARM_T = "parameters"
REMN_T = "remainder"
STOR_T = "storage"
SYM_T = "symbol"
TELM_T = "telemetry"  # Location specific information
TOK_T = "tokens"
TYPE_T = "type"
VAL_T = "value"

# Token type values
DEF = "DEFINE"
EQU = "EQU"
INST = "INSTRUCTION"
LBL = "LABEL"
MULT = "MULTIPLE"
ORG = "ORIGIN"
SEC = "SECTION"
STOR = "STORAGE"
SYM = "SYMBOL"
DIR = "DIRECTIVE"
BAD = "INVALID"

MAX_SYMBOL_LENGTH = 25

LOGGER_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'

DIRECTIVES = [
    "DEF",
    "ENDM",
    "ENDU",
    "EXPORT",
    "GLOBAL",
    "INCBIN",
    "MACRO",
    "NEXTU",
    "ORG",
    "Purge",
    "SECTION",
    "SET",
    "UNION",
]

STORAGE_DIRECTIVES = [
    "DS",
    "DB",
    "DW",
    "DL"
]

MEMORY_DIRECTIVES = [
    "WRAM0",
    "VRAM",
    "ROMX",
    "ROM0",
    "HRAM",
    "WRAMX",
    "SRAM",
    "OAM"
]

MEMORY_OPTIONS = [
    "BANK",
    "ALIGN"
]

REGISTERS = [
    # General Purpose Registers. A is the Accumulator
    "A", "B", "C", "D", "E", "F", "H", "L",
    # Register Pairs
    "BC", "DE", "HL"
]

DEFINE_OPERATORS = [
    "=",
    "EQU",
    "EQUS"
]

PUNCTUATORS = "\"'([{}])+"
QUOTE_PUNCTUATORS = "\"'"
BEGIN_PUNCTUATORS = "([{"
END_PUNCTUATORS = ")]}"

DPair = namedtuple("DPair", ('begin', 'end'))
DelimData = namedtuple("DelimData", ('start', 'end', 'd_pair', 'label'))

DELIMITER_PAIRS = [
    DPair("'", "'"),
    DPair('"', '"'),
    DPair("[", "]"),
    DPair("(", ")"),
    DPair("{", "}")
]

#
# Bracketing is also done by " and ' which is why they are part of
# this array.
# BRACKETS = "\"'([{}])"


class Lexical(IntEnum):
    """Lexical error types."""

    WARNING = 1
    SYNTAX_ERROR = 2
    UNKNOWN_ERROR = 3


NodeType = Enum('NodeType', ['DEF',    # Define
                             'EQU',    # Equate
                             'INST',   # Instruction
                             'LBL',    # Label
                             'ORG',    # Origin
                             'PARM',   # Parameter
                             'SEC',    # Section
                             'STOR',   # Storage
                             'SYM',    # Symbol
                             'NODE'])  # Node


NODE_TYPES = {
    NodeType.NODE: NODE_T,  # Internal type, not a compiler diective
    NodeType.PARM: PARM_T,  # Internal type, not a compiler diective
    NodeType.EQU: EQU,
    NodeType.LBL: LBL,
    NodeType.SYM: SYM,
    NodeType.INST: INST,
    NodeType.STOR: STOR,
    NodeType.SEC: SEC,
    NodeType.ORG: ORG,
    NodeType.DEF: DEF,
}

AddressRange = namedtuple("AddressRange", ["start", "end"])


class AddressType(Enum):
    """Enumerate list of memory address types."""

    AbsolueAddress = auto()
    RelativeAddress = auto()


@dataclass
class NodeDefinition:
    """Hold the definition values of a Node for the compiler."""

    directive: str = "UNASSIGNED"
    identifier: str = None
    address_type: AddressType = AddressType.AbsolueAddress
    address_range: AddressRange = AddressRange(start=0, end=0)
    length: int = 0


class MinMax(NamedTuple):
    """Represent a min and max value in a single object."""

    min: int
    max: int

    def __repr__(self) -> str:
        """Return string representation of this object."""
        return f"<MinMax(min={self.min}, max={self.max})>"


MAX_16BIT_VALUE = 0xffff
MAX_8BIT_VALUE = 0xff

# NODE_FORMAT = {
# ORG: { "Directive": ORG,
# "Identifier": None,  # String
# "AddressType": AddressType.AbsolueAddress,
# "Address": AddressSpread}
# EQU: {}
# }
