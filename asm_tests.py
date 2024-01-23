"""GameBoy assembler unit tests."""
import unittest
import sys
from dmg_asm.tests.core_tests import ExpressionUnitTests, ConvertUnitTests, \
    DescriptorUnitTests, SymbolUnitTests
from dmg_asm.tests.token_tests import TokenUnitTests
from dmg_asm.tests.directive_tests import DirectiveUnitTests
from dmg_asm.tests.symbol_label_resolver_tests import SymbolAndLabelUnitTests
from dmg_asm.tests.instruction_tests import InstructionDecodingTests
from dmg_asm.tests.ip_tests import IPUnitTests


# ---------------------------------------------------------------
print("===== Instruction Decoding Unit Tests ===============")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(InstructionDecodingTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("===== Descriptor Tests ==============================")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(DescriptorUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("===== Expression Tests ==============================")
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(ExpressionUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("=============== Conversion Unit Tests ===============")
suite = loader.loadTestsFromTestCase(ConvertUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("=============== Symbol Unit Tests ===============")
suite = loader.loadTestsFromTestCase(SymbolUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("=============== Token Unit Tests ===============")
suite = loader.loadTestsFromTestCase(TokenUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("=============== Directive Unit Tests ===============")
suite = loader.loadTestsFromTestCase(DirectiveUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("============ Symbol and Label Unit Tests ============")
suite = loader.loadTestsFromTestCase(SymbolAndLabelUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)

# ---------------------------------------------------------------
print("============ Instruction Pointer Tests ==============")
suite = loader.loadTestsFromTestCase(IPUnitTests)
unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
