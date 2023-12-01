"""DMG Assembler unit tests."""

# import os
import unittest

from ..core.convert import ExpressionConversion
from ..core.expression import Expression, ExpressionType
from ..core.exception import ExpressionBoundsError, ExpressionSyntaxError


class ExpressionUnitTests(unittest.TestCase):
    """Expression Unit Tests"""

    def test_valid_hex_expr(self):
        """Test hex expression."""
        try:
            expr1 = Expression("0x1A0B")
        except ExpressionSyntaxError:
            self.fail("Expression Syntax Error")
        except ExpressionBoundsError:
            self.fail("Expression bounds error.")
        self.assertTrue(expr1.value == "1A0B")

        try:
            expr2 = Expression("$F2")
        except ExpressionSyntaxError:
            self.fail("Hex value $F2 failed to parse.")
        except ExpressionBoundsError:
            self.fail("Hex value $F2 failed bounds check.")
        self.assertTrue(expr2.value == "F2")

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

    def test_character_type(self):
        """Test label expression."""
        try:
            expr = Expression("'Hello'")
        except (ExpressionBoundsError, ExpressionSyntaxError):
            self.fail("Unable to parse 'Hello' expression")
        self.assertTrue(expr.type == ExpressionType.CHARACTER)

#  End of unit tests
