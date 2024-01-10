"""Class(es) that construct a Z80 mnemonic from tokens."""

from dataclasses import dataclass
from icecream import ic
from ..core import Convert
from ..core.expression import Expression
from ..core.exception import DescriptorException, ExpressionSyntaxError
from ..tokens import TokenGroup, Token, TokenType, Tokenizer
from .instruction_set import InstructionSet as IS, InstructionDetail
from .registers import Registers


class Mnemonic:
    """Represent a Z80 instruction."""

    __slots__ = ('opcode', 'token_group', 'instruction_detail',
                 'elements')
    opcode: str
    token_group: TokenGroup
    instruction_detail: InstructionDetail
    elements: list

    def __init__(self, tokenized_instruction: TokenGroup):
        """Initialize a mnemonic with an instruction that has been
        tokenized."""
        if tokenized_instruction is None or len(tokenized_instruction) == 0:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        if tokenized_instruction[0].type != TokenType.KEYWORD:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        self.token_group = tokenized_instruction
        self.opcode = None
        self.elements = None
        self.instruction_detail = self._instruction_detail

    def __repr__(self):
        """Return the string representation of how this object is created."""
        return f"Mnemonic({self.token_group})"

    def __str__(self):
        """Return a print-friendly representation of this object."""
        return str(self.instruction_detail)

    @property
    def _instruction_detail(self) -> InstructionDetail:
        """Evaluate the token group into an identified mnemonic."""
        self.elements = self._listify(self.token_group)
        length = len(self.elements)
        self.opcode = self.elements[0]
        node = IS().instruction_from_mnemonic(self.opcode)
        operands = []
        index = 1
        detail = None
        while node is not None and length >= index:
            if "!" in node:
                hex_str = Convert(Expression(f"0{node['!']}")).to_hex_string()
                detail = IS().instruction_detail_from_byte(hex_str.lower())
                if len(operands) > 0:
                    detail.operand1 = operands[0]

                if len(operands) > 1:
                    detail.operand2 = operands[1]
                break
            element = self.elements[index]
            if node is not None and "!" not in node:
                node = self._assign_operand(element, node)
                operands.append(element)
            index += 1
        return detail

    def _assign_operand(self, operand, node) -> dict:
        if "!" in node:
            return node
        if operand in node:
            return node[operand]
        if Expression.has_valid_prefix(operand):
            idx = self.token_group.find_first_value(operand)
            if idx is not None:
                tok = self.token_group[idx]
                new_node = self._data_placeholder(node, tok.data)
                return new_node
        if Registers().is_valid_register(operand):
            new_node = self._register_placeholder(node, operand)
            return new_node
        return None

    def _data_placeholder(self, node: dict, expression: Expression) -> dict:
        """Convert an expression into a corresponding placeholder.

        Placeholders are ["d8", "d16", "a8", "a16"]
        """
        #
        # Get the maximum value of the expression...
        # item = [x for x in placeholders if x in text]
        maxi = expression.descriptor.args.limits.max-1
        # get the number of bits for that max value (should be 8 or 16)
        bits = f'{maxi:b}'
        dkey = f'd{len(bits)}'
        akey = f'a{len(bits)}'
        if dkey in node:
            return node[dkey]
        if akey in node:
            return node[akey]
        return None
        # item = [x for x in placeholders if x in text]

    def _register_placeholder(self, node: dict, register: str) -> dict:
        """Convert a register into a corresponding placeholder.

        So a register like 'H' will return a placeholder of 'r8' whereas a
        register like 'SP' will return an 'r16'. This only works because single
        length register names are always 8 bit and two are always 16 bit.
        """
        length = len(register)
        rkey = "r8" if length == 1 else "r16" if length == 2 else None
        if rkey is not None:
            return node[rkey]
        return None

    def _listify(self, token_group: TokenGroup) -> list:
        """Create a list of values from a token group.

        The main difference of this list vs. a token_group list is that
        an element will combine delimeters '(' or ')' into a single element
        whereas a token group keeps these values distinct.

        For the purposes of the mnemonic, it's important to turn a list like:
        ['(', 'HL', ')']
        into a single element "(HL)".
        """
        elements = []
        value = ""
        in_paren = False
        for token in token_group:
            if token.value == "(":
                in_paren = True
            elif token.value == ")":
                in_paren = False
            value += token.value.upper()
            if in_paren is False:
                elements.append(value)
                value = ""
        return elements
