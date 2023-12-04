"""Convert an Expression to/from decimal (unless it's a character type)."""

from .expression import Expression


class Convert:
    """Class to convert an exression from one base to another."""

    def __init__(self, expr: Expression):
        """Initialize the Convert object."""
        if not expr.is_valid():
            err = "Input Expression object is not in a valid state."
            raise ValueError(err)
        self._expr = expr
        self._value_str = expr.value
        self._value_base = expr.descriptor.args.base
        self._dec_value = int(self._value_str, self._value_base)

    def to_decimal(self) -> Expression:
        """Convert expression to a decimial valued expression."""
        pad = "02d" if self._dec_value < 100 else "04d"
        return Expression(f"0{self._dec_value:{pad}}")

    def to_hex16(self) -> Expression:
        """Convert expression to a 16-bit hexidecimal value."""
        return Expression(f"${self._dec_value:04X}")

    def to_hex(self) -> Expression:
        """Convert expression to an 8-bit hexidecimal value."""
        return Expression(f"${self._dec_value:02X}")

    def to_octal(self) -> Expression:
        """Convert expression to an Octal value."""
        return Expression(f"&{self._dec_value:o}")

    def to_binary(self) -> Expression:
        """Convert expression to an Binary value."""
        return Expression(f"%{self._dec_value:08b}")

# Class Convert.py ends here.
