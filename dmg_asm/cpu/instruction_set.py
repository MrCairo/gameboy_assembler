"""Class(es) that implements a Z80/LR35902 instruction and Instruction Set."""

import io
import json
from dataclasses import dataclass, make_dataclass

from .LR35902.lr35902_data import LR35902Data
from ..core.expression import Expression
from ..core.exception import DescriptorException, ExpressionSyntaxError


@dataclass
class InstructionDetail:
    """Represent detail data of an instruction.

    All fields excluding the immediate flags are represented in the LR35902
    CPU data fields.
    immediate1 and 2 are used to flag whether operand1 or 2, repectively,
    are immediate data like a relative byte, 16-bit data or address. These
    values are set in the Mnemonics object when an instruction is parsed.
    Users of the Mnemonics class can then determine how the object should be
    represented 1, 2, or 3 bytes and when operand represents the data.
    """

    # __slots__ = ('addr', 'cycles', 'flags', 'length', 'mnemonic',
    #              'operand1', 'operand2')
    addr: str
    cycles = []
    flags = []
    length = 0
    mnemonic: str = ""
    operand1: str = None
    operand2: str = None
    # Either one immediate is True if their corresponding operand is a
    # data placeholder - meaning that it will required compile-time data.
    immediate1: bool = False  # True if operand1 is immediate (placeholder)
    immediate2: bool = False  # True if operand2 is immediate data
    # Used to hold binary representation of the entire instruction after
    # parsing.
    code: bytes = None


#
# Special internal functions to generate a Python dictionary from JSON
#
def _gen_lr35902_inst() -> dict:
    # -------------------------------------------------------
    def _load_cpu_data() -> dict:
        try:
            return json.load(io.StringIO(LR35902Data().json))
        except json.JSONDecodeError:
            return None
    # -------------------------------------------------------

    raw_data = _load_cpu_data()

    if raw_data is None:
        return None

    instructions = {}

    # This creates a 'shorthand' version of the LR35902 instruction set that
    # makes it easier to look up and parse.

    for hex_code in raw_data:
        node = raw_data[hex_code]
        mnemonic = node['mnemonic'] if 'mnemonic' in node else None
        if mnemonic is None or mnemonic == "PREFIX":
            continue
        try:
            expr = Expression(hex_code).integer_value
            term = {"!": expr}
        except (ExpressionSyntaxError, DescriptorException, ValueError):
            print(f"Invalid hex code: {hex_code}")
            term = {"!": "00"}
        op1 = node["operand1"] if "operand1" in node else None
        op2 = node["operand2"] if "operand2" in node else None

        existing = {} if mnemonic not in instructions \
            else instructions[mnemonic]

        line = term
        if op1 is not None:
            # Compute what the final line will be:
            #   Only op1:
            #       "JR": {"r8": {"!": 0x18}
            #   Op1 and Op2:
            #       "LD":  {"BC": {"d16": {"!": 0x01}}
            line = {op1: term} if op2 is None else {op1: {op2: term}}
            if op1 not in existing:
                existing[op1] = line[op1]
            else:
                existing[op1].update(line[op1])
        else:
            # Handles mnemonics without op codes:
            #   "NOP": {"!": 0x00}
            existing = line
        instructions[mnemonic] = existing
    # End for
    return {"instructions": instructions, "raw_data": raw_data}

# ############################################################################


# @singleton
class InstructionSet():
    """The LR35902 CPU instruction set.

    This represents the LR35902 CPU instruction set and is implemented
    as a singleton object. The instruction set returned is done in a type
    of 'shorthand' that makes parsing and traversing easy.

    Example:
    -------
    'ADD': { 'A': { '(HL)': { '!': 0x86 }}}
        'LD': { '(a16)': { 'A': { '!': 0xea }}}
        'CPL': { '!': 0x2f }

    Addresses and register placeholders in the instruction set are defined
    as follows:

      d8:  Immediate 8-bit data.

      d16: Immediate 16-bit data.

      a8:  8 bit unsigned data, which are added to $FF00 in certain
           instructions (replacement for missing IN and OUT instructions).

      a16: 16-bit address

      r8:  8-bit signed data which are added to the program counter.

    For an instruction key value is "!":
      !    Represents the end of instruction data mostly made for the internal
           mnemonic roamer. If lets the roamer know when it has reached the end
           of a specific mnemonic within the dictionary list.

           It's value represents the Opcode of the mnemonic.
    """

    __slots__ = ('data', 'lr35902', 'lr35902_detail')
    placeholders = ["a8", "a16", "d8", "d16", "r8"]

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(InstructionSet, cls).__new__(cls)
            cls.instance.data = _gen_lr35902_inst()
            cls.instance.lr35902 = cls.instance.data["instructions"]
            cls.instance.lr35902_detail = cls.instance.data["raw_data"]
        return cls.instance

    def instruction_from_mnemonic(self, mnemonic: str) -> dict:
        """Get the instruction definition dict for the given mnemonic."""
        return self.lr35902[mnemonic] if mnemonic in self.lr35902 else None

    def instruction_detail_from_byte(self, byte: str) -> InstructionDetail:
        """Get the instruction detail from a specific byte."""
        detail: InstructionDetail = None
        data = self.lr35902_detail[byte] \
            if byte in self.lr35902_detail else None
        if data:
            detail = make_dataclass(
                "InstructionDetail", ((k, type(v)) for k, v
                                      in data.items()))(**data)
            detail.addr = Expression(detail.addr)
            if hasattr(detail, 'operand1'):
                detail.immediate1 = detail.operand1 in self.placeholders
            if hasattr(detail, 'operand2'):
                detail.immediate2 = detail.operand2 in self.placeholders
        return detail

    @property
    def instruction_set(self):
        """Get the Z80 instruction set as a dictionary."""
        return self.lr35902

    def is_mnemonic(self, mnemonic_string: str) -> bool:
        """Test if the string represent a mnemonic."""
        return mnemonic_string.lower() in self.lr35902

    #                                             #
    # -----=====<  Private Functions  >=====----- #

    def _merge(self, target, source):
        """Merge target and source."""
        return source if target is None else {**target, **source}

# --------========[ End of InstructionSet class ]========-------- #


# if __name__ == "__main__":
#    import pprint
#    pp = pprint.PrettyPrinter(indent=4, compact=False, width=40)
#    pp.pprint(InstructionSet().LR35902)
