"""Class(es) that construct a Z80 mnemonic from tokens."""

from dataclasses import dataclass
from icecream import ic
from ..core import Convert
from ..core.expression import Expression
from ..core.exception import ExpressionBoundsError, ExpressionSyntaxError
from ..tokens import TokenGroup, Token, TokenType, Tokenizer
from .instruction_set import InstructionSet as IS, InstructionDetail
from .registers import Registers


class Mnemonic:
    """Represent a Z80 instruction."""

    __slots__ = ('opcode', 'operands', 'token_group', 'elements',
                 'instruction_detail')

    def __init__(self, mnemonic_tokens: TokenGroup):
        if mnemonic_tokens is None or len(mnemonic_tokens) == 0:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        if mnemonic_tokens[0].type != TokenType.KEYWORD:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        self.token_group = mnemonic_tokens
        self.opcode = None
        self.operands = []
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
        index = 0
        element = self.elements[index]
        self.opcode = element
        node = IS().instruction_from_mnemonic(self.opcode)
        if node is None:
            return None

        # If the instruction does not have operands (i.e. NOP) then
        self.operands = []
        index = 1
        detail = None
        while length >= index:
            if "!" in node:
                hex_str = Convert(node["!"]).to_hex_string()
                detail = IS().instruction_detail_from_byte(hex_str.lower())
                if len(self.operands) > 0:
                    detail.operand1 = self.operands[0]
                if len(self.operands) > 1:
                    detail.operand2 = self.operands[1]
                break
            element = self.elements[index]
            if node is not None and "!" not in node:
                node = self._assign_operand(element, node)
                # element = expr if expr is not None else element
                self.operands.append(element)
            index += 1
        return detail

    def _assign_operand(self, item, node) -> dict:
        if "!" in node.keys():
            return node
        if item in node.keys():
            return node[item]
        if Expression.has_valid_prefix(item):
            idx = self.token_group.find_first_value(item)
            if idx is not None:
                tok = self.token_group[idx]
                new_node = self._data_placeholder(node, tok.data)
                return new_node
        if Registers().is_valid_register(item):
            new_node = self._register_placeholder(node, item)
            return new_node
        return None

    def _data_placeholder(self, node: dict, expression: Expression) -> dict:
        # placeholders = ["d8", "d16", "a8", "a16", "r8"]
        # Get the maximum value of the expression...
        # item = [x for x in placeholders if x in text]
        maxi = expression.descriptor.args.limits.max
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
        length = len(register)
        rkey = "r8" if length == 1 else "r16" if length == 2 else None
        if rkey is not None:
            return node[rkey]
        return None

    def _listify(self, token_group: TokenGroup) -> list:
        """Create a list of values from a token group."""
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
