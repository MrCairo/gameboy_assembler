"""Class(es) that implements a Z80/LR35902 instruction and Instruction Set."""

import io
import json
from dataclasses import dataclass, make_dataclass

from .LR35902.lr35902_data import LR35902Data
from ..core.convert import Convert
from ..core.expression import Expression
from ..core.exception import ExpressionBoundsError, ExpressionSyntaxError


@dataclass
class InstructionDetail:
    # __slots__ = ('addr', 'cycles', 'flags', 'length', 'mnemonic',
    #              'operand1', 'operand2')
    addr: str
    cycles = []
    flags = []
    length = 0
    mnemonic = ""
    operand1 = None
    operand2 = None


#
# Special internal functions to generate a Python dictionary from JSON
#
def _gen_LR35902_inst() -> dict:
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
            conv = Convert(Expression(hex_code))
            expr = conv.to_decimal()
            term = {"!": expr}
        except ExpressionSyntaxError:
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

    Examples:
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

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(InstructionSet, cls).__new__(cls)
            cls.instance.data = _gen_LR35902_inst()
            cls.instance.lr35902 = cls.instance.data["instructions"]
            cls.instance.lr35902_detail = cls.instance.data["raw_data"]
        return cls.instance

    def __init__(self):
        """Initialize the InstructionSet object."""
        # self.data = _gen_LR35902_inst()
        # self.lr35902 = self.data["instructions"]
        # self.lr35902_detail = self.data["raw_data"]
        # -----=====< End of __init__() >=====----- #

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
        return detail

    @property
    def instruction_set(self):
        """Get the Z80 instruction set as a dictionary."""
        return self.lr35902

    def is_mnemonic(self, mnemonic_string: str) -> bool:
        """Test if the string represent a mnemonic."""
        return mnemonic_string.upper() in self.lr35902

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
