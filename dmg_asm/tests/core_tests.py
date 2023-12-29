"""DMG Assembler unit tests."""

# import os
import unittest

from ..core.convert import Convert
from ..core.expression import ExpressionType, Expression
from ..core.exception import ExpressionBoundsError, ExpressionSyntaxError


class ConvertUnitTests(unittest.TestCase):
    """Expression Conversion Unit Tests."""

    def test_8bit_hex_expr_conversion(self):
        """Test decimal conversion to an 8-bit hex value."""
        expr = Expression("0100")
        try:
            expr_hex = Convert(expr).to_hex()
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to hex.")
        else:
            self.assertTrue(expr_hex.clean_str == "$64")

    def test_16bit_hex_expr_conversion(self):
        """Test decimal conversion to a 16-bit hex value."""
        expr = Expression("0100")
        try:
            expr_hex = Convert(expr).to_hex16()
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to hex.")
        else:
            self.assertTrue(expr_hex.clean_str == "$0064")

    def test_octal_expr_conversion(self):
        """Test decimal conversion to an 8-bit octal value."""
        expr = Expression("0100")
        try:
            expr_oct = Convert(expr).to_octal()
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to octal.")
        else:
            self.assertTrue(expr_oct.clean_str == "&144")

    def test_binary_expr_conversion(self):
        """Test decimal conversion to an 8-bit binary value."""
        expr = Expression("0100")
        try:
            expr_bin = Convert(expr).to_binary()
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to binary.")
        else:
            self.assertTrue(expr_bin.clean_str == "%01100100")


class ExpressionUnitTests(unittest.TestCase):
    """Expression Unit Tests."""

    def test_valid_16bit_hex_expr(self):
        """Test 16-bit hex expression."""
        try:
            expr1 = Expression("0x1A0B")
        except ExpressionSyntaxError:
            self.fail("Expression Syntax Error")
        except ExpressionBoundsError:
            self.fail("Expression bounds error.")
        self.assertTrue(expr1.prefixless_value == "1A0B")

        try:
            expr1 = Expression("$$BAAD")
        except ExpressionSyntaxError:
            self.fail("Expression Syntax Error")
        except ExpressionBoundsError:
            self.fail("Expression bounds error.")
        self.assertTrue(expr1.prefixless_value == "BAAD")

    def test_valid_8bit_hex_expr(self):
        """Test 8-bit hex expression."""
        try:
            expr2 = Expression("$F2")
        except ExpressionSyntaxError:
            self.fail("Hex value $F2 failed to parse.")
        except ExpressionBoundsError:
            self.fail("Hex value $F2 failed bounds check.")
        self.assertTrue(expr2.prefixless_value == "F2")

    def test_invalid_hex_expr(self):
        """Test invalid hex expression."""
        try:
            Expression("0xHZKL")
        except ExpressionSyntaxError as syntax:
            self.assertTrue(len(syntax.args) >= 1)
        else:
            self.fail("Hex 0xHZKL was not flagged as invalid")

        try:
            Expression("$FFD210")
        except ExpressionBoundsError as bounds:
            self.assertTrue(len(bounds.args) >= 1)
        else:
            self.fail("$FFD210 was not flagged with a bounds error.")

    def test_hex_type(self):
        """Test hex expression type."""
        try:
            expr = Expression("$1A")
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable to parse $1A")
        self.assertTrue(expr.type == ExpressionType.HEXIDECIMAL)

    def test_octal_type(self):
        """Test octal expression."""
        try:
            expr = Expression("&10")
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable to parse &10")
        self.assertTrue(expr.type == ExpressionType.OCTAL)

    def test_binary_type(self):
        """Test binary expression."""
        try:
            expr = Expression("%10011101")
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable to parse binary value")
        self.assertTrue(expr.type == ExpressionType.BINARY)

    def test_invalid_binary_expression(self):
        """Test if an invalid binary expression fails properly."""
        try:
            Expression("%100111001")
        except ExpressionBoundsError as bounds:
            self.assertTrue(len(bounds.args) >= 1)
        else:
            self.fail("%100111001 did not generate a bounds exception.")

    def test_label_type(self):
        """Test label expression."""
        try:
            expr = Expression("'Hello'")
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable to parse 'Hello' expression")
        self.assertTrue(expr.type == ExpressionType.CHARACTER)

    def test_invalid_label_expr(self):
        """Test an invalid label properly fails."""
        try:
            Expression("'Hello World\"")
        except ExpressionSyntaxError as syntax:
            self.assertTrue(len(syntax.args) > 0)
        else:
            self.fail("Invalid label passed validation.")

#  End of unit tests
