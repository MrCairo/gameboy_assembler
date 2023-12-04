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
from dataclasses import dataclass

from .descriptor import HEX_DSC, HEX16_DSC, BIN_DSC, OCT_DSC, DEC_DSC
from .descriptor import LBL_DSC, BaseDescriptor
from .exception import ExpressionSyntaxError, ExpressionBoundsError


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
    """Parse and categorize a numerical expression."""

    def __init__(self, exp_str: str):
        """Initialize an Expression object with a specific value."""
        if exp_str is None:
            raise ExpressionSyntaxError("Initial value cannot be None")
        self._result = Validator.validate(exp_str)
        self._expr = self._result.pwords.join()

    def __repr__(self):
        """Return a representation of this object and how to re-create it."""
        desc = ""
        if self._result is not None and self._result.is_valid():
            desc = f"Expression({self._expr})"
        else:
            desc = f"Invalid: Expression({self._expr})"
        return desc

    def __str__(self):
        """Return a String representation of the object."""
        desc = ""
        if self._result is not None and self._result.is_valid():
            desc = str(self._result)
        else:
            desc = "Object not initialized or is not valid."
        return desc

    def is_valid(self) -> bool:
        """Return a bool indicating if this Expression is valid."""
        return self._result.is_valid()

    @property
    def value(self) -> str:
        """Return the value of the expression without the prefix."""
        return self._result.pwords.word

    @property
    def type(self) -> ExpressionType:
        """Return the type of this expression."""
        return self._result.type

    @property
    def prefix(self) -> str:
        """Return the prefix of this expression."""
        return self._result.pwords.prefix

    @property
    def descriptor(self) -> BaseDescriptor:
        """Return the descriptor identified for this expression."""
        return self._result.descriptor

    @property
    def raw_str(self) -> str:
        """Return the raw (or cleaned) value of the expression."""
        return self._result.pwords.join()

    # |++++++++++++++++++++++++++++++++++++++++++++++++++++++++|

    @dataclass(frozen=True)
    class Elements:
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
    class Components:
        """Represent an expressions evaluated components."""

        descriptor: BaseDescriptor
        type: ExpressionType
        pwords: 'Expression.Elements'

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


# Shorthand
EXEL = Expression.Elements
EXCO = Expression.Components

# |-----------------============<***>=============-----------------|
#
# This is the class that is used to validate an expression. It's meant to be
# local to this module and never exported.
#


class Validator:
    """Class that handles Expression Validation."""

    _prefixes = ["0x", "0", "$$", "$", "&", "%", "'", '"']

    @classmethod
    def validate(cls, expr_str: str) -> Expression.Components:
        """Validate the expression and return an ExprComponents object.

        Arguments:
        expr_str -- The expression as a string (i.e. 0xABCD, %10110011)
        """
        if expr_str is None:
            raise ExpressionSyntaxError("Missing expression string.")

        expr = expr_str.strip()
        components = cls.get_expr_components(expr)
        descr = components.descriptor

        # If any characters are NOT in the allowed charactset, fail.
        cls.try_in_charset(components)

        # Our range is inclusive of the max whereas the Python range()
        # is exclusive. The +1 over the limit accounts for this.
        cls.try_len_range(components)

        # Ignore base of 0 which is a Label.
        if descr.args.base > 0:
            cls.try_val_range(components)

        # If we get here, the expression is valid.
        return components

    #
    # Validation Functions
    #
    @staticmethod
    def try_len_range(source: Expression.Components):
        """Test if expression is within args.chars.min/max length."""
        value = source.pwords.word
        descr = source.descriptor
        if len(value) not in range(descr.args.chars.min,
                                   descr.args.chars.max+1):
            msg = "Expression length is outside of length bounds"
            raise ExpressionBoundsError(msg)

    @staticmethod
    def try_val_range(source: Expression.Components):
        """Test if expression is within min/max value limits."""
        value = source.pwords.word
        descr = source.descriptor
        num = int(value, descr.args.base)
        if not descr.args.limits.max >= num >= descr.args.limits.min:
            msg = "Expression value is outside predefined bounds: "
            msg += f"[{source.pwords.join()}]"
            raise ExpressionBoundsError(msg)

    @staticmethod
    def try_in_charset(source: Expression.Components):
        """Test if expression uses invalid characters for its type."""
        descr = source.descriptor
        word = source.pwords.word
        bad = [x for x in word if x not in descr.args.charset]
        if len(bad):
            msg = f"Invalid character in expression: [{word}:{bad}]"
            raise ExpressionSyntaxError(msg)

    #
    # Helper Functions
    #
    @classmethod
    def get_expr_components(cls, expr_str: str) -> Expression.Components:
        """Return the descriptor and expression type of the value passed."""
        if expr_str is None:
            raise ExpressionSyntaxError("Missing expression string.")

        expr = expr_str.strip()
        if len(expr) < 3:  # 3 is the min size of an expression (ex. $AB).
            msg = f"Expression length must be > 2: [{expr}]"
            raise ExpressionSyntaxError(msg)

        #
        # While there is an 'is_valid()' function for pwords, we check
        # individual values so that an appropriate exception can be thrown if
        # necessary.
        #
        pwords = cls._split_expr(expr)
        if pwords.prefix is None:
            msg = f"Invalid prefix in expression: [{expr}]"
            raise ExpressionSyntaxError(msg)

        # Check for a string/label suffix value (i.e. "Label") The suffix
        # needs to be equal to the prefix. The _split_expr function will set
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

        return Expression.Components(descriptor, expr_type, pwords)

    @classmethod
    def _split_expr(cls, expr: str) -> Expression.Elements:
        """Split the expression into prefix and suffic parts."""
        _key = [x for idx,
                x in enumerate(cls._prefixes) if expr.startswith(x)]
        if _key is None:
            return Expression.Elements(None, None, None)
        prefix = _key[0]
        # A string's suffix must be an exact match to the prefix.
        suffix = ""
        if prefix in ["'", '"']:
            suffix = prefix if expr.endswith(prefix) else None
            if suffix is None:
                return Expression.Elements(prefix, None, None)
        word = expr.removeprefix(prefix).removesuffix(suffix)
        return Expression.Elements(prefix, word, suffix)

# |-----------------============<***>=============-----------------|

# expression.py ends here.
