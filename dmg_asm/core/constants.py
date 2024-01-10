"""Commonly used constants."""

from dataclasses import dataclass
from collections import namedtuple
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
    "SECTION",
    "WRAM0",
    "VRAM",
    "ROMX",
    "ROM0"
    "HRAM",
    "WRAMX",
    "SRAM",
    "OAM",
    "BANK",
    "ALIGN"
]

DEFINE_OPERATORS = [
    "=",
    "EQU",
    "EQUS"
]

PUNCTUATORS = "\"'([{}])"
#
# Bracketing is also done by " and ' which is why they are part of
# this array.
# BRACKETS = "\"'([{}])"


class Lexical(IntEnum):
    """Lexical error types."""

    warning = 1
    syntax_error = 2
    unknown_error = 3


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


@dataclass
class MinMax:
    """Represent a min and max value in a single object."""

    min: int
    max: int

    def __str__(self) -> str:
        """Return string representation of this object."""
        return f"MinMax(min={self.min}, max={self.max})"


# NODE_FORMAT = {
# ORG: { "Directive": ORG,
# "Identifier": None,  # String
# "AddressType": AddressType.AbsolueAddress,
# "Address": AddressSpread}
# EQU: {}
# }
