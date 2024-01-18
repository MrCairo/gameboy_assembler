"""A numeric or string value expression.

Represents a validated expression.
An expression is like:
    0xFFFF
    $AABC
    %010101
    &1777
    "MY_LABEL"
"""
# from enum import StrEnum
from __future__ import annotations
from dataclasses import dataclass

from .descriptor import HEX_DSC, HEX16_DSC, BIN_DSC, OCT_DSC, DEC_DSC
from .descriptor import LBL_DSC, BaseDescriptor
from .exception import ExpressionSyntaxError, \
    DescriptorException


@dataclass
class ExpressionType:
    """The expression type."""

    BINARY = 'binary'
    CHARACTER = 'character'
    DECIMAL = 'decimal'
    HEXIDECIMAL = 'hexidecimal'
    INVALID = 'invalid'
    OCTAL = 'octal'

# |-----------------============<***>=============-----------------|

# It's important what order the prefixes appear in the array.  The '0x', for
# example, should be found before '0'. By doing this, we reduce the
# additional validation. If the array were defined with '0' first, there
# would need to be another check to see if there is an 'x' following the 0
# or if it's just 0 (decimal vs. hex definition).


class Expression:
    """Parse and categorize a numerical expression.

    Expression prefixes are as follows:
    +-------+---------------------------------------------------------------+
    | $, 0x | An 8 or 16-bit hexidecimal value. Must be at least two digits.|
    +-------+---------------------------------------------------------------+
    |   $$  | A 16-bit hexidecimal value only. Must be 4 digits in length.  |
    +-------+---------------------------------------------------------------+
    |   0   | A decimal value. Must be at least two digits (001 for 1)      |
    +-------+---------------------------------------------------------------+
    |   %   | An 8-bit only binary digit (i.e %10101011)                    |
    +-------+---------------------------------------------------------------+
    | ", '  | Encloses a Symbolic string expression. Must start and end with|
    |       | the same character. 'Hello' "World"                           |
    +-------+---------------------------------------------------------------+
    |   &   | An 8-bit octal value.                                         |
    +-------+---------------------------------------------------------------+
    """

    __slots__ = ("_components", "_int_value")

    def __init__(self, exp_str: str):
        """Initialize an Expression object with a specific value."""
        if exp_str is None:
            raise ValueError("Initial value cannot be None")
        try:
            self._components = _Validator().validate(exp_str)
        except (ValueError, TypeError, DescriptorException) as err:
            raise err
        except ExpressionSyntaxError as syntax_err:
            raise syntax_err
        if self._components is None:
            msg = f'"{exp_str}" is not a valid Expression.'
            raise ExpressionSyntaxError(msg)
        self._int_value = -1  # -1 means unintialized.
        _ = self.integer_value

    def __repr__(self):
        """Return a representation of this object and how to re-create it."""
        desc = ""
        if self._components is not None and self._components.is_valid():
            desc = f"Expression({self.clean_str})"
        else:
            desc = f"Invalid: Expression({self.clean_str})"
        return desc

    def __str__(self):
        """Return a String representation of the object."""
        desc = ""
        if self._components is not None and self._components.is_valid():
            desc = str(self._components)
        else:
            desc = "Object not initialized or is not valid."
        return desc

    def __eq__(self, other) -> bool:
        """Return equality value (==)."""
        if isinstance(other, Expression):
            return self.integer_value == other.integer_value
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.integer_value != other.integer_value
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.integer_value < other.integer_value
        return False

    def __le__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.integer_value <= other.integer_value
        return False

    def __gt__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.integer_value > other.integer_value
        return False

    def __ge__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.integer_value >= other.integer_value
        return False

    @property
    def integer_value(self) -> int:
        """Return the positive decimal integer value of this Expression."""
        if self._int_value == -1:  # -1 == uninitialized
            _value_str = self.prefixless_value
            _value_base = self.descriptor.args.base
            if _value_base != 0:
                self._int_value = int(_value_str, _value_base)
        return self._int_value

    @classmethod
    def has_valid_prefix(cls, expr: str) -> bool:
        """Return True if the expression string starts with a prefix."""
        return _Validator.has_valid_prefix(expr)

    @property
    def prefixless_value(self) -> str:
        """Return the value of the expression without the prefix.

        A call to this function that has the expression of $0100 will result
        in a returned string of 0100.

        Also, a value with a prefix an suffix (i.e. "String") will be returned
        without a prefix NOR a suffix - "Hello" is returned as Hello
        """
        return self._components.pwords.word

    @property
    def type(self) -> ExpressionType:
        """Return the type of this expression."""
        return self._components.type

    @property
    def prefix(self) -> str:
        """Return the prefix of this expression."""
        return self._components.pwords.prefix

    @property
    def descriptor(self) -> BaseDescriptor:
        """Return the descriptor identified for this expression."""
        return self._components.descriptor

    @property
    def clean_str(self) -> str:
        """Return the cleaned expression and includes prefix/suffix values."""
        return self._components.pwords.join()

    # |++++++++++++++++++++++++++++++++++++++++++++++++++++++++|


@dataclass(frozen=True)
class _Elements:
    """Represent an expression's parts - prefix, word, and suffix."""

    prefix: str
    word: str  # The value of the expression sans affixes.
    suffix: str

    def __str__(self) -> str:
        """Return formatted string of this object."""
        desc = f"Elements: ( [{self.prefix}] "
        desc += self.word
        desc += f" [{self.suffix}] )" if self.suffix else " )"
        return desc

    def is_valid(self) -> bool:
        """Return true if the object is valid."""
        valid = self.prefix is not None and len(self.prefix) > 0 \
            and self.suffix is not None \
            and self.word is not None and len(self.word) > 0
        return valid

    def join(self) -> str:
        """Join together a split expression."""
        joined = self.prefix+self.word+self.suffix
        return joined if self.is_valid() else None

    # |++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++|


@dataclass(frozen=True)
class _Components:
    """Represent an expressions evaluated components."""

    descriptor: BaseDescriptor
    type: ExpressionType
    pwords: _Elements

    def __str__(self) -> str:
        """Return string representation of this object."""
        desc = f"Components(type={self.type}, "
        desc += f"descr={str(self.descriptor)}, "
        desc += f"pwords={str(self.pwords)})\n"
        return desc

    def is_valid(self) -> bool:
        """Return true if the object is valid."""
        if self.descriptor is None or self.type is None:
            return False
        if self.pwords is None:
            return False
        return self.pwords.is_valid()

# |-----------------============<***>=============-----------------|
#
# This is the class that is used to validate an expression. It's meant to be
# local to this module and never exported.
#


class _Validator:
    """Class that handles Expression Validation."""

    _prefixes = ["0x", "0", "$$", "$", "&", "%", "'", '"']

    # The value isn't important but we need to assign this variable something
    # so that it will be set as a class variable. It's important so that it
    # can then be used as a descriptor/validator.
    value: BaseDescriptor = HEX_DSC

    @classmethod
    def has_valid_prefix(cls, expr: str) -> bool:
        """Return True if the expression string starts with a prefix."""
        elements = _Validator.get_elements(expr)
        return elements.prefix is not None

    def validate(self, expr_str: str) -> _Components:
        """Validate the expression and return an ExprComponents object.

        Arguments:
        expr_str -- The expression as a string (i.e. 0xABCD, %10110011)
        """
        if expr_str is None:
            raise ValueError("Missing expression string.")

        expr = expr_str.strip()
        components = _Validator.get_expr_components(expr)
        if components.descriptor:
            # Update the class variable's descriptor definition
            _Validator.value = components.descriptor
            # Assign the value to the instance of the class variable which will
            # trigger the descriptor to validate the expr_str. If invalid, the
            # descriptor will raise an exception.
            self.value = components.pwords.word
            return components
        return None

    #
    # Helper Functions
    #
    @classmethod
    def get_expr_components(cls, expr_str: str) -> _Components:
        """Return the descriptor and expression type of the value passed."""
        if expr_str is None:
            raise ValueError("Missing expression string.")

        expr = expr_str.strip()
        if len(expr) < 3:  # 3 is the min size of an expression (ex. $AB).
            msg = f"Expression length must be > 2: [{expr}]"
            raise ExpressionSyntaxError(msg)

        #
        # While there is an 'is_valid()' function for pwords, we check
        # individual values so that an appropriate exception can be thrown if
        # necessary.
        #
        pwords = cls.get_elements(expr)
        if pwords.prefix is None:
            msg = f"Invalid prefix in expression: [{expr}]"
            raise ExpressionSyntaxError(msg)

        # Check for a string/label suffix value (i.e. "Label") The suffix
        # needs to be equal to the prefix. The split_expr function will set
        # suffix to None if the affixes don't match or are not present.
        if pwords.suffix is None:
            msg = f"Mismatched string affix [{expr}]"
            raise ExpressionSyntaxError(msg)

        match pwords.prefix:
            case "$" | "0x":
                descriptor = HEX16_DSC if len(pwords.word) > 2 else HEX_DSC
                expr_type = ExpressionType.HEXIDECIMAL
            case "$$":
                descriptor = HEX16_DSC
                expr_type = ExpressionType.HEXIDECIMAL
            case "0":
                descriptor = DEC_DSC
                expr_type = ExpressionType.DECIMAL
            case '"' | "'":
                descriptor = LBL_DSC
                expr_type = ExpressionType.CHARACTER
            case "%":
                descriptor = BIN_DSC
                expr_type = ExpressionType.BINARY
            case "&":
                descriptor = OCT_DSC
                expr_type = ExpressionType.OCTAL
            case _:
                msg = f"Expression prefix is invalid [{expr}]"
                raise ExpressionSyntaxError(msg)

        return _Components(descriptor, expr_type, pwords)

    @classmethod
    def get_elements(cls, expr: str) -> _Elements:
        """Split the expression into prefix and suffic parts."""
        _key = [x for idx,
                x in enumerate(cls._prefixes) if expr.startswith(x)]
        if _key is None or len(_key) == 0:
            return _Elements(None, None, None)
        prefix = _key[0]
        # A string's suffix must be an exact match to the prefix.
        suffix = ""
        if prefix in ["'", '"']:
            suffix = prefix if expr.endswith(prefix) else None
            if suffix is None:
                return _Elements(prefix, None, None)
        word = expr.removeprefix(prefix).removesuffix(suffix)
        return _Elements(prefix, word, suffix)

# |-----------------============<***>=============-----------------|

# expression.py ends here.
