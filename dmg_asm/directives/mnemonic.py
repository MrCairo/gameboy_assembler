"""Class(es) that construct a Z80 mnemonic from tokens."""

# pylint: disable=relative-beyond-top-level
from ..core.exception import ExpressionSyntaxError
from ..core import Convert, Label, Labels, Symbol, Symbols, Expression
from ..tokens import TokenGroup, TokenType
from ..cpu.instruction_set import InstructionSet as IS, InstructionDetail


class Mnemonic:
    """Represent a Z80 instruction with operands with custom data/addresses.

    This class is instantiated with a group of tokens that begin with a
    token of the type INSTRUCTION. If this is not the case, this object will
    raise an ExpressionSyntaxError exception.

    Once instantiated, the `instruction_detail` will contain the parsed and
    resolved instruction as found in the lr35902 instruction data. If
    `instruction_detail` is None, then the token group contained a malformed
    instruction.

    In addition to parse, this class will also resolve and SYMBOL or LABEL
    values included. SYMBOL and LABEL values must be re-resolved if they
    change and they can do that via the `resolve_again()` method.
    """

    __slots__ = ('token_group', 'instruction_detail')
    token_group: TokenGroup
    instruction_detail: InstructionDetail

    def __init__(self, tokens: TokenGroup):
        """Initialize a mnemonic with an instruction that has been
        tokenized."""
        if tokens is None or len(tokens) == 0:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        if tokens[0].type != TokenType.INSTRUCTION:
            raise ExpressionSyntaxError("Invalid Mnemonic")
        self.token_group = tokens
        self.instruction_detail = _Utils.instruction_detail(tokens)

    def __repr__(self):
        """Return the string representation of how this object is created."""
        return f"Mnemonic({self.token_group})"

    def __str__(self):
        """Return a print-friendly representation of this object."""
        return str(self.instruction_detail)

    @property
    def opcode(self) -> str | None:
        """Return the opcode of this instruction.

        The 'mnemonic' value in the instruction detail is the same as this
        Mnemonic's Opcode.
        """
        if self.instruction_detail:
            return self.instruction_detail.mnemonic
        return None

    def resolve_again(self):
        """Force the Mnemonic to re-resolve it's initial tokens.

        This will force, for example, re-evaluating the Symbols and Labels
        which would be necessary if they have changed since this object was
        created."""
        self.instruction_detail = _Utils.instruction_detail(self.token_group)

# --------========[ End of Mnemonic class ]========-------- #


class _Utils:
    """Utilities for the Mnemonic class implemented as a singleton."""

    data_placeholders = ["a8", "a16", "d8", "d16", "r8"]

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(_Utils, cls).__new__(cls)
        return cls.instance

    @classmethod
    def has_data_placeholder(cls, text: str) -> bool:
        """Return whether or not a data placeholder is in the passed text."""
        found = [x for x in _Utils.data_placeholders if x in text]
        return len(found) > 0

    @classmethod
    def find_matching_placeholders(cls, text: str, value: str) -> [str]:
        """Replace a placeholder in a string with a specific value.

        Note: the expression must be a valid range of the placeholder. For
        example, an 8-bit placeholder cannot be replaced with a 16-bit value.
        """
        if Expression.has_valid_prefix(value) is False:
            return []
        expr = Expression(value)
        maxi = expr.descriptor.args.limits.max-1
        # get the number of bits for that max value (should be 8 or 16)
        bits = f'{maxi:b}'
        dkey = f'd{len(bits)}'
        akey = f'a{len(bits)}'

        # Never a r16, only 8-bit relative signed value.
        rkey = "r8" if len(bits) == 8 else None

        result = [text.replace(value, dkey),
                  text.replace(value, akey)]
        if rkey:
            result.append(text.replace(value, rkey))
        return result

    @classmethod
    def data_placeholder_node(cls,
                              node: dict, expression: Expression) -> dict:
        """Convert an expression into a corresponding placeholder.

        Placeholders are ["d8", "d16", "a8", "a16", "r8"]
        """
        if node is None or expression is None:
            return None

        #
        # Get the maximum value of the expression...
        # item = [x for x in placeholders if x in text]
        maxi = expression.descriptor.args.limits.max-1
        # get the number of bits for that max value (should be 8 or 16)
        bits = f'{maxi:b}'
        dkey = f'd{len(bits)}'
        akey = f'a{len(bits)}'
        rkey = "r8"  # Never a r16, only 8-bit relative signed value.

        afound = [x for x in node.keys() if akey in x]
        if len(afound):
            return node[afound[0]]

        dfound = [x for x in node.keys() if dkey in x]
        if len(dfound):
            return node[dfound[0]]

        rfound = [x for x in node.keys() if rkey in x]
        if len(rfound):
            return node[rfound[0]]

        return None
        # item = [x for x in placeholders if x in text]

    @classmethod
    def listify(cls, token_group: TokenGroup) -> (list, dict):
        """Create a list of values from a token group.

        The main difference of this list vs. a token_group list is that
        an element will combine delimeters '(' or ')' into a single element
        whereas a token group keeps these values distinct.

        For the purposes of the mnemonic, it's important to turn a list like:
        ['(', 'HL', ')']
        into a single element "(HL)".
        """
        elements = []
        special = {}
        value = ""
        plus = False  # If encountered, smush addends together
        in_paren = False
        for token in token_group:
            if token.value == "(":
                in_paren = True
            elif token.value == ")":
                in_paren = False
            elif token.value == "+":
                plus = True
                value = elements.pop()  # Append next value to previous element
            elif plus is True:
                plus = False
                value = elements.pop()
                special[value+token.value.lower()] = token.value
            value += token.value.lower()
            if in_paren is False:
                elements.append(value)
                value = ""
        return (elements, special)

    @classmethod
    def instruction_detail(cls, token_group: TokenGroup) -> InstructionDetail:
        """Return the detail of the decoded instruction.

        A 'None' will be returned if the token group couldn't be decoded."""
        (elements, special) = _Utils.listify(token_group)
        length = len(elements)
        if length == 0:
            return None
        node = IS().instruction_from_mnemonic(elements[0])
        operands = []
        index = 1
        detail = None
        while node is not None and index <= length:
            if "!" in node:
                detail = _Utils._complete_node(operands, node)
                break
            operand = elements[index]
            if node is not None and "!" not in node:
                node = _Utils._assignments(token_group, special,
                                           operand, node)
                if node is not None:
                    label = node.pop("__label_value", None)
                    operand = str(label) if label else operand
                operands.append(operand)
            index += 1
        return detail

    @classmethod
    def _assignments(cls, tokens: TokenGroup, special: dict,
                     operand: str, node: dict) -> dict:
        new_node = cls._assign_if_special(special, operand, node)
        if new_node:
            return new_node
        new_node = cls._assign_if_exact(operand, node)
        if new_node:
            return new_node
        new_node = cls._assign_if_expression(tokens, operand, node)
        if new_node:
            return new_node
        new_node = cls._assign_if_label(operand, node)
        if new_node:
            return new_node
        new_node = cls._assign_if_symbol(operand, node)
        if new_node:
            return new_node
        return None

    @classmethod
    def _assign_if_special(cls, special: dict, operand: str,
                           node: dict) -> dict:
        """Special is basically something like SP+LABEL or ($FF00+C)."""
        if len(special) > 0 and operand in special:
            _label_value = ""
            to_find: str = special.pop(operand)
            # Special should be able to be converted to an Expression.
            if Expression.has_valid_prefix(to_find) is False:
                # if not, this special value could be a label. Resolve it.
                label: Label = Labels().find(to_find)
                if label:
                    to_find = Convert(label.value).to_hex_string()
                    operand = operand.replace(label.name.lower(), to_find)
                    # Let downstream know we replaced the element's label
                    _label_value = operand
            found = _Utils.find_matching_placeholders(operand,
                                                      to_find)
            sus = [x for x in found if x in node]
            if len(sus) and len(_label_value) > 0:
                node[sus[0]]["__label_value"] = _label_value
            return node[sus[0]] if len(sus) else None
        return None

    @classmethod
    def _assign_if_exact(cls, operand: str, node: dict) -> dict:
        if operand.lower() in node:
            return node[operand]
        return None

    @classmethod
    def _assign_if_expression(cls, tokens: TokenGroup,
                              operand: str, node: dict) -> dict:
        plain = operand.strip("()")
        if Expression.has_valid_prefix(plain):
            idx = tokens.find_first_value(plain)
            if idx is not None:
                tok = tokens[idx]
                new_node = _Utils.data_placeholder_node(node, tok.data)
                return new_node
        return None

    @classmethod
    def _assign_if_label(cls, operand: str, node: dict) -> dict:
        plain = operand.strip("()")
        label: Label = Labels().find(plain)
        if label:
            new_node = _Utils.data_placeholder_node(node, label.value)
            if new_node is not None:
                hexi = Convert(label.value).to_hex_string()
                operand = operand.replace(plain, hexi)
                new_node['__label_value'] = operand
            return new_node
        return None

    @classmethod
    def _assign_if_symbol(cls, operand: str, node: dict) -> dict:
        plain = operand.strip("()")
        symbol: Symbol = Symbols().find(plain)
        if symbol:
            new_node = _Utils.data_placeholder_node(node,
                                                    symbol.base_address)
            if new_node is not None:
                hexi = Convert(symbol.base_address).to_hex_string()
                operand = operand.replace(plain, hexi)
                new_node['__label_value'] = operand
            return new_node
        return None

    @classmethod
    def _resolve_if_label(cls, text: str) -> Expression | None:
        label: Label = Labels().find(text)
        return label.value if label else None

    @classmethod
    def _complete_node(cls, operands: list, node: dict) -> InstructionDetail:
        """Complete the node parsing.

        This function assumes that `node` points to a '!' value."""
        hex_str = Convert(Expression(f"0{node['!']}")).to_hex_string()
        detail = IS().instruction_detail_from_byte(hex_str.lower())
        # Convert the actual operand into what was parsed by the Mnemonic.
        if detail and len(operands) > 0:
            detail.operand1 = operands[0]
        if detail and len(operands) > 1:
            detail.operand2 = operands[1]
        code = Convert(detail.addr).to_code()
        if hasattr(detail, 'immediate1') and detail.immediate1:
            code += Convert(Expression(detail.operand1)).to_code()
        if hasattr(detail, 'immediate2') and detail.immediate2:
            code += Convert(Expression(detail.operand2)).to_code()
        detail.code = code
        return detail
