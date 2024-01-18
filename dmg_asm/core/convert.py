"""Convert an Expression to/from decimal (unless it's a character type)."""

from .expression import Expression


class Convert:
    """Class to convert an exression from one base to another."""

    # __slots__ = ('_expr', '_value_str', '_value_base', 'dec_value')
    # _expr: Expression
    # _value_str: str
    # _value_base: int
    # _dec_value: int

    def __init__(self, expr: Expression):
        """Initialize the Convert object."""
        self._expr: Expression = expr
        self._value_str: str = expr.prefixless_value
        self._value_base: int = expr.descriptor.args.base
        self._dec_value: int = int(self._value_str, self._value_base)

    def to_decimal_int(self) -> int:
        """Return the decimal equivalent of the expression."""
        return self._dec_value

    def to_decimal(self) -> Expression:
        """Convert expression to a decimial valued expression."""
        pad = "02d" if self._dec_value < 100 else "04d"
        return Expression(f"0{self._dec_value:{pad}}")

    def to_hex16(self) -> Expression:
        """Convert expression to a 16-bit hexidecimal value."""
        return Expression(f"${self._dec_value:04X}")

    def to_hex16_string(self) -> str:
        """Convert the expression to a 16-bit hex string with a '$' prefix."""
        return f"${self._dec_value:04X}"

    def to_hex(self) -> Expression:
        """Convert expression to an 8-bit hexidecimal value."""
        return Expression(f"${self._dec_value:02X}")

    def to_hex_string(self) -> str:
        """Convert the expression to an 8-bit hex string with a '$' prefix."""
        if self._dec_value > 256:
            return self.to_hex16_string()
        return f"${self._dec_value:02X}"

    def to_octal(self) -> Expression:
        """Convert expression to an Octal value."""
        return Expression(f"&{self._dec_value:o}")

    def to_binary(self) -> Expression:
        """Convert expression to an Binary value."""
        return Expression(f"%{self._dec_value:08b}")

    def to_code(self) -> bytes | None:
        """Convert to bytes. 16-bit values are written as LSB MSB."""
        val: int = self.to_decimal_int()
        code = None
        if self._value_base == 0:
            text = self._expr.value
            code = text.encoding()
        elif self._expr.descriptor.args.limits.max-1 > 255:
            code = val.to_bytes(2, byteorder='little')
        elif self._expr.descriptor.args.limits.max-1 < 256:
            code = val.to_bytes(1)
        return code


# Class Convert.py ends here.
