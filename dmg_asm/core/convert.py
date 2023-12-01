"""Convert an Expression to/from decimal (unless it's a character type)."""

import string
from singleton_decorator import singleton
from collections import namedtuple

from .expression import ExpressionType, Expression

ECMinMax = namedtuple('ECMinMax', ['min', 'max'])


@singleton
class ExpressionConversion():
    """Convert value from a non-decimal expression to a decimal value.

    Class to convert a numeric type from one base to/from decimal.
    When an expression is provided or requested, it will have one of
    these previx values:

    '$' -- Hex value. If the decimal value is less than 256, the value
           returned will be a single byte. A value between 256 and 65535
           inclusive will return two bytes in big endian format.

    '0' -- A decimal value

    '%' -- A binary value.
    """

    def __init__(self):
        """Initialze a conversion object."""
        self._to_dec = {
            '$': self._hex_to_dec,
            '0': self._dec,
            '%': self._bin_to_dec,
            '&': self._oct_to_dec,
            '0x': self._hex_to_dec
        }
        self._from_dec = {
            '$': self._dec_to_hex,
            '$$': self._dec_to_hex16,
            '0': self._dec_to_dec,
            '%': self._dec_to_bin,
            '&': self._dec_to_oct,
            '0x': self._dec_to_hex
        }
        self._8_bit_registers = ['B', 'C', 'D', 'E', 'H', 'L', 'A']
        self._16_bit_registers = ['BC', 'DE', 'HL', 'F', 'PC', 'SP']
        self._internal_type: ExpressionType = ExpressionType.INVALID

    def expression_from_decimal(self,
                                dec_value,
                                expression_prefix) -> Expression:
        """Return a converted decimal value based upon the prefix.

        expression_prefix -- This represents the data type to convert the
        provided decimal value to.
        """
        try:
            dec_value = dec_value + 0  # Ensure that this is a numeric value
        except TypeError:
            return None

        if expression_prefix in self._from_dec:
            conv = self._from_dec[expression_prefix]
            return Expression(conv(dec_value))
        return ""

    def decimal_from_expression(self, expression: Expression):
        """Convert a given expression to it's decimal equivalent.

        Expressions:
          Hexadecimal: $0123456789ABCDEF. Case-insensitive
          Decimal: 0123456789
          Octal: &01234567
          Binary: %01
          Fixedpoint (16.16): 01234.56789
          Character constant: "ABYZ"
          Gameboy graphics: '0123

        Note: CHARACTER expressions return None
        """
        if not expression:
            return None

        key = expression.prefix
        conv = None if key not in self._to_dec else self._to_dec[key]
        if conv and expression.type is not ExpressionType.CHARACTER:
            return conv(expression)
        return None

    def can_convert(self, expression: Expression):
        """Return the decimal equivalent of 'expression'."""
        return self.decimal_from_expression(expression) is not None

    def has_valid_prefix(self, expression: Expression):
        """Return True if the expression contains is a supported prefix."""
        # An Expression object, if it is instantiated, cannot be invalid.
        return True if expression is not None else False

    # def hex_to_high_low(self, hex_value):
    #     new_value = None
    #     dec = self._hex_to_dec(hex_value)
    #     if dec is not None:
    #         high = dec & 0xff00
    #         low = dec & 0x00ff
    #         new_value = self._dec_to_hex(high)
    #         new_value = self._dec_to_hex
    #     return new_value

    # def hex_high_byte(self, hex_value):
    #     new_value = None
    #     dec = self._hex_to_dec(hex_value)
    #     if dec is not None:
    #         new_value = self._dec_to_hex16(dec & 0xff00)
    #     return new_value

    def _hex_to_dec(self, val):
        """Convert a hexidecimal number ($12, $1234) into a decimal value."""
        hexi = "0123456789ABCDEF"
        if not self._validate_expression(val, '$', ECMinMax(1, 10), hexi):
            return None
        self._internal_type = ExpressionType.HEXIDECIMAL
        return int(val[1:], 16)

    def _dec_to_hex(self, val, digits=2):
        """Convert a decimal value into it's hexidecimal equivalent."""
        try:
            clean = val + 0
        except TypeError:
            return None
        # Validate ranges
        if digits not in [2, 4]:
            digits = 2
        clean = max(clean, 0)
        if clean > 255:
            digits = 4
        if clean >= 16 ** digits:
            clean = (16 ** digits) - 1
        hex_str = hex(clean)[2:]
        padded = "$" + hex_str.zfill(digits)
        self._internal_type = ExpressionType.DECIMAL
        return padded

    def _dec_to_hex16(self, val):
        """Return a decimal value into it's 16-bit decimal equivalent."""
        return self._dec_to_hex(val, digits=4)

    def _dec(self, val):
        """Validate and return the value as a decimal number."""
        if not self._validate_expression(val,
                                         '0',
                                         ECMinMax(1, 10), "0123456789"):
            return None

        return int(val[1:], 10)

    def _dec_to_dec(self, val):
        """Convert dec val to string with a leading 0.

        Return a decimal value as a string with a leading 0 (123 =
        0123). This is used primarily to convert a value as it would appear as
        an expression. Like a hex value starts with '$', a decimal value
        starts with '0'.
        """
        try:
            clean = max(0, min(65535, val))
        except TypeError:
            return None
        self._internal_type = ExpressionType.DECIMAL
        return "0" + str(clean)

    def _bin_to_dec(self, val):
        """Validate and convert binary value to a decimal value.

        Validate the binary value and return as a decimal number.
        The binary value (%1001) can be from 1 bit to a max of 16 bits.
        """
        if not self._validate_expression(val, '%', ECMinMax(1, 16), "01"):
            return None

        self._internal_type = ExpressionType.BINARY
        return int(val[1:], 2)

    def _dec_to_bin(self, val) -> str:
        """Convert a decimal value to a binary value in string format.

        Returns the binary representation of the provided decimal value.
        Returns a 0 if < 0, 65535 if > 65535
        """
        clean = max(0, min(65535, val))
        self._internal_type = ExpressionType.BINARY
        return '%' + bin(clean)[2:]

    def _oct_to_dec(self, val):
        """Convert the octal value to it's Decimalequivalent.

        Validate the octal value and return as a decimal number.
        The binary value (%1001) can be from 1 bit to a max of 16 bits.
        """
        if not self._validate_expression(val, '&', (1, 5), "01234567"):
            return None
        self._internal_type = ExpressionType.DECIMAL
        return int(val[1:], 8)

    def _dec_to_oct(self, val):
        """Convert the decimal value to it's Octal equivalent."""
        try:
            clean = max(0, min(65535, val))
        except TypeError:
            return None
        self._internal_type = ExpressionType.OCTAL
        return '&' + oct(clean)[2:]

    def _validate_expression(self, exp, key, minmax: ECMinMax, chrset):
        mini = minmax.min
        maxi = minmax.max
        if not exp or exp[:len(key)] != key:
            return False

        val = exp[1:]
        if len(val) < mini or len(val) > maxi:
            return False

        for char in val:
            if char.upper() not in chrset:
                return False
        return True

    def _is_hex(self, expression):
        if expression:
            return expression.strip()[0] == "$"
        return False

    def _is_character(self, expression: str):
        """Return True if the expression is a character expression."""
        """
        A character expression type must begin and end
        with double-quotes. It's a string.
        """
        dquotes = expression.startswith('"') and expression.endswith('"')
        squotes = expression.startswith("'") and expression.endswith("'")
        return dquotes or squotes

    #
    # Kind of a dup of the InstructionSet().is_valid_register() function.
    # Probably move the InstructionSet one to here since we don't want
    # instruction.py and conversions.py to cross reference each other.
    #

    def _is_register(self, expression):
        is_reg = False
        if expression:
            upcase = expression.upper()
            if upcase in self._8_bit_registers:
                is_reg = True
            elif upcase in self._16_bit_registers:
                is_reg = True
        return is_reg

# End of class ExpressionConversion #
