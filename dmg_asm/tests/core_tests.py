"""DMG Assembler unit tests."""

# import os
import unittest

from ..core.convert import Convert
from ..core.symbol import Symbol, SymbolScope, Symbols
from ..core.expression import ExpressionType, Expression
from ..core.descriptor import BaseDescriptor, BaseValue, HEX_DSC, HEX16_DSC, \
    DEC_DSC, BIN_DSC, OCT_DSC, LBL_DSC
from ..core.constants import MinMax
from ..core.exception import ExpressionSyntaxError, \
    InvalidSymbolName, InvalidSymbolScope, \
    DescriptorMinMaxLengthError, \
    DescriptorMinMaxValueError, \
    DescriptorRadixDigitValueError, \
    DescriptorRadixError, \
    DescriptorException


class ConvertUnitTests(unittest.TestCase):
    """Expression Conversion Unit Tests."""

    def test_8bit_hex_expr_conversion(self):
        """Test decimal conversion to an 8-bit hex value."""
        expr = Expression("0100")
        try:
            expr_hex = Convert(expr).to_hex()
        except (DescriptorException, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to hex.")
        else:
            self.assertTrue(expr_hex.clean_str == "$64")

    def test_16bit_hex_expr_conversion(self):
        """Test decimal conversion to a 16-bit hex value."""
        expr = Expression("0100")
        try:
            expr_hex = Convert(expr).to_hex16()
        except (DescriptorException, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to hex.")
        else:
            self.assertTrue(expr_hex.clean_str == "$0064")

    def test_octal_expr_conversion(self):
        """Test decimal conversion to an 8-bit octal value."""
        expr = Expression("0100")
        try:
            expr_oct = Convert(expr).to_octal()
        except (DescriptorException, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to octal.")
        else:
            self.assertTrue(expr_oct.clean_str == "&144")

    def test_binary_expr_conversion(self):
        """Test decimal conversion to an 8-bit binary value."""
        expr = Expression("0100")
        try:
            expr_bin = Convert(expr).to_binary()
        except (DescriptorException, ExpressionSyntaxError):
            self.fail("Unable convert decimal 0100 to binary.")
        else:
            self.assertTrue(expr_bin.clean_str == "%01100100")


class DescriptorUnitTests(unittest.TestCase):
    """Descriptor unit tests."""

    dec_value = DEC_DSC
    hex_value = HEX_DSC

    generic: BaseDescriptor = None

    def test_decimal_descriptor(self):
        self.dec_value = "100"
        try:
            self.hex_value = "AF"
        except (TypeError, ValueError, DescriptorException) as err:
            self.fail(err)
        try:
            self.hex_value = "ABCD"
        except (TypeError, ValueError, DescriptorException):
            pass
        else:
            self.fail("The 8-bit hex value descriptor assignment failed.")

        DescriptorUnitTests.generic = BaseDescriptor(chars=MinMax(2, 5),
                                                     limits=MinMax(0, 65536),
                                                     base=16)
        try:
            self.generic = "FFFE"
        except (TypeError, ValueError, DescriptorException) as err:
            self.fail(err)

        DescriptorUnitTests.generic = HEX16_DSC
        try:
            self.generic = "AHGB"
        except (TypeError, ValueError, DescriptorException):
            pass
        else:
            self.fail("AHGB isn't a valid 16-bit hex value but passed.")


class ExpressionUnitTests(unittest.TestCase):
    """Expression Unit Tests."""

    def test_valid_16bit_hex_expr(self):
        """Test 16-bit hex expression."""
        try:
            expr1 = Expression("0x1A0B")
        except ExpressionSyntaxError:
            self.fail("Expression Syntax Error")
        except DescriptorException:
            self.fail("Expression bounds error.")
        self.assertTrue(expr1.prefixless_value == "1A0B")

        try:
            expr1 = Expression("$$BAAD")
        except ExpressionSyntaxError:
            self.fail("Expression Syntax Error")
        except DescriptorException:
            self.fail("Expression bounds error.")
        self.assertTrue(expr1.prefixless_value == "BAAD")

    def test_valid_8bit_hex_expr(self):
        """Test 8-bit hex expression."""
        try:
            expr2 = Expression("$F2")
        except ExpressionSyntaxError:
            self.fail("Hex value $F2 failed to parse.")
        except DescriptorException:
            self.fail("Hex value $F2 failed bounds check.")
        self.assertTrue(expr2.prefixless_value == "F2")

    def test_invalid_hex_expr(self):
        """Test invalid hex expression."""
        try:
            Expression("0xHZKL")
        except DescriptorRadixDigitValueError as syntax:
            self.assertTrue(len(syntax.args) >= 1)
        else:
            self.fail("Hex 0xHZKL was not flagged as invalid")

        try:
            Expression("$FFD210")
        except DescriptorMinMaxLengthError as bounds:
            self.assertTrue(len(bounds.args) >= 1)
        else:
            self.fail("$FFD210 was not flagged with a bounds error.")

    def test_hex_type(self):
        """Test hex expression type."""
        try:
            expr = Expression("$1A")
        except (DescriptorException, TypeError, ValueError):
            self.fail("Unable to parse $1A")
        self.assertTrue(expr.type == ExpressionType.HEXIDECIMAL)

    def test_octal_type(self):
        """Test octal expression."""
        try:
            expr = Expression("&10")
        except (DescriptorException, TypeError, ValueError):
            self.fail("Unable to parse &10")
        self.assertTrue(expr.type == ExpressionType.OCTAL)

    def test_binary_type(self):
        """Test binary expression."""
        try:
            expr = Expression("%10011101")
        except (DescriptorException, ValueError, TypeError):
            self.fail("Unable to parse binary value")
        self.assertTrue(expr.type == ExpressionType.BINARY)

    def test_invalid_binary_expression(self):
        """Test if an invalid binary expression fails properly."""
        try:
            Expression("%100111001")
        except DescriptorMinMaxLengthError as bounds:
            print(bounds)
        else:
            self.fail("%100111001 did not generate a bounds exception.")

    def test_label_type(self):
        """Test label expression."""
        try:
            expr = Expression("'Hello'")
        except (DescriptorException, ExpressionSyntaxError):
            self.fail("Unable to parse 'Hello' expression")
        self.assertTrue(expr.type == ExpressionType.CHARACTER)

    def test_invalid_label_expr(self):
        """Test an invalid label properly fails."""
        try:
            Expression("'Hello World\"")
        except (DescriptorException, ExpressionSyntaxError) as syntax:
            self.assertTrue(len(syntax.args) > 0)
        else:
            self.fail("Invalid label passed validation.")


class SymbolUnitTests(unittest.TestCase):
    """Symbol unit tests."""

    def test_valid_symbol_name(self):
        """Test that a valid symbol name passes validation."""
        name = "Valid_symbol:"
        sym = Symbol(name, Expression("0x1000"))
        self.assertTrue(sym.clean_name == "Valid_symbol")
        self.assertTrue(sym.scope == SymbolScope.LOCAL)
        self.assertTrue(sym.base_address == Expression("$1000"))

    def test_invalid_symbol_names(self):
        """Pass if name is detected as invalid."""
        invalid_name = "42Fun:"
        try:
            _ = Symbol(invalid_name, Expression("$0100"))
        except InvalidSymbolName:
            pass
        except (TypeError, InvalidSymbolScope):
            self.fail("Symbol with invalid name raised wrong exception.")
        else:
            self.fail("An invalid symbol name failed vailidation.")

        invalid_name = ".no-hypens-allowed"
        try:
            _ = Symbol(invalid_name, Expression("$00FF"))
        except InvalidSymbolName:
            pass
        except (TypeError, InvalidSymbolScope):
            self.fail("Symbol with invalid name raised wrong exception.")
        else:
            self.fail("An invalid symbol name failed vailidation.")

        invalid_name = ".local_global::"
        try:
            _ = Symbol(invalid_name, Expression("$00FF"))
        except InvalidSymbolScope:
            pass
        except (TypeError, InvalidSymbolName):
            self.fail("Symbol with invalid scope raised wrong exception.")
        else:
            self.fail("An invalid symbol name failed vailidation.")

    def test_private_scope_is_valid(self):
        """Test valid private scope."""
        name = ".private_scope:"
        try:
            symbol = Symbol(name, Expression("$FFD2"))
        except (TypeError, InvalidSymbolName, InvalidSymbolScope):
            self.fail("Valid private scope failed validation.")
        self.assertTrue(symbol.scope == SymbolScope.PRIVATE)

    def test_local_scope_is_valid(self):
        """Test valid local scope."""
        name = "local_scope:"
        try:
            symbol = Symbol(name, Expression("$FFD2"))
        except (TypeError, InvalidSymbolName, InvalidSymbolScope):
            self.fail("Valid local scope failed validation.")
        self.assertTrue(symbol.scope == SymbolScope.LOCAL)

    def test_global_scope_is_valid(self):
        """Test valid global scope."""
        name = "global_scope::"
        try:
            symbol = Symbol(name, Expression("$FFD2"))
        except (TypeError, InvalidSymbolName, InvalidSymbolScope):
            self.fail("Valid global scope failed validation.")
        self.assertTrue(symbol.scope == SymbolScope.GLOBAL)


#  End of unit tests
