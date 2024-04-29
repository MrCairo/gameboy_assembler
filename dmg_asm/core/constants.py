"""Commonly used constants."""

import os
from dataclasses import dataclass
from collections import namedtuple
from typing import NamedTuple
from enum import auto, Enum

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
    "INCLUDE",
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
    "DW"
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
ZERO_STR = "000"

DPair = namedtuple("DPair", ('begin', 'end'))
DelimData = namedtuple("DelimData", ('start', 'end', 'd_pair', 'label'))

DELIMITER_PAIRS = [
    DPair("'", "'"),
    DPair('"', '"'),
    DPair("[", "]"),
    DPair("(", ")"),
    DPair("{", "}")
]

NUMERIC_BASES = [2, 8, 10, 16]


class StorageType(Enum):
    """Represent the storage class storage size type."""

    BLOCK = auto()
    BYTE = auto()
    WORD = auto()
    LONG = auto()

#
# Bracketing is also done by " and ' which is why they are part of
# this array.
# BRACKETS = "\"'([{}])"


class MinMax(NamedTuple):
    """Represent a min and max value in a single object."""

    min: int
    max: int

    def __repr__(self) -> str:
        """Return string representation of this object."""
        return f"<MinMax(min={self.min}, max={self.max})>"


MAX_16BIT_VALUE = 0xffff
MAX_8BIT_VALUE = 0xff


@dataclass
class Environment:
    """A set of values that the compiler/assembler uses to operate."""

    project_dir: str = None  # Absolute path to the project
    source_dir: str = None   # Source dir relative to project_dir
    include_dir: str = None  # Include source relative to project_dir

    def __init__(self, project_dir: str = os.getcwd(),
                 source_dir: str = None,
                 include_dir: str = None):
        """Initialize the object."""
        if project_dir is None or len(project_dir) == 0:
            self.project_dir = os.getcwd()
        else:
            self.project_dir = project_dir
        self.source_dir = source_dir if source_dir else ""
        self.include_dir = include_dir if include_dir else ""

# NODE_FORMAT = {
# ORG: { "Directive": ORG,
# "Identifier": None,  # String
# "AddressType": AddressType.AbsolueAddress,
# "Address": AddressSpread}
# EQU: {}
# }
