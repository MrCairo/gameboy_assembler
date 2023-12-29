"""GameBoy assembler unit tests."""
import unittest
import sys
from dmg_asm.tests.core_tests import ExpressionUnitTests, ConvertUnitTests
from dmg_asm.tests.token_tests import TokenUnitTests
from dmg_asm.tests.directive_tests import DirectiveUnitTests

# ---------------------------------------------------------------
print("\nExpression Tests")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(ExpressionUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("\nConversion Unit Tests")
suite = loader.loadTestsFromTestCase(ConvertUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)


# ---------------------------------------------------------------
print("\nToken Unit Tests.")
# suite = unittest.TestSuite()
# suite.addTest(TokenUnitTests('test_tokenize_lines'))
# suite.addTest(TokenUnitTests('test_token_group_from_string'))
# suite.addTest(TokenUnitTests('test_token_group_from_elements'))
suite = loader.loadTestsFromTestCase(TokenUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("\nDirective Unit Tests.")
suite = unittest.TestSuite()
suite.addTest(DirectiveUnitTests('test_equate_from_string'))
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
