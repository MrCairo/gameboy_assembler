"""GameBoy assembler unit tests."""
import unittest
import sys
from dmg_asm.tests.core_tests import ExpressionUnitTests, ConvertUnitTests, \
    DescriptorUnitTests, SymbolUnitTests
from dmg_asm.tests.token_tests import TokenUnitTests
from dmg_asm.tests.directive_tests import DirectiveUnitTests
from dmg_asm.tests.symbol_label_resolver_tests import SymbolAndLabelUnitTests
from dmg_asm.tests.instruction_tests import InstructionDecodingTests


# ---------------------------------------------------------------
print("\n========== Instruction Decoding Unit Tests ==========")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(InstructionDecodingTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Descriptor Tests ===============")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(DescriptorUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Expression Tests ===============")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(ExpressionUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Conversion Unit Tests ===============")
suite = loader.loadTestsFromTestCase(ConvertUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Symbol Unit Tests ===============")
suite = loader.loadTestsFromTestCase(SymbolUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Token Unit Tests ===============")
suite = loader.loadTestsFromTestCase(TokenUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n=============== Directive Unit Tests ===============")
suite = loader.loadTestsFromTestCase(DirectiveUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)

# ---------------------------------------------------------------
print("\n============ Symbol and Label Unit Tests ============")
suite = loader.loadTestsFromTestCase(SymbolAndLabelUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
