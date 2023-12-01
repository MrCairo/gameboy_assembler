""" DMG Unit Testing runner """
import unittest
from dmg_asm.tests.core_tests import ExpressionUnitTests

print("\nExpression Tests")
suite = unittest.TestLoader().loadTestsFromTestCase(ExpressionUnitTests)
unittest.TextTestRunner(verbosity=2).run(suite)


# tests.py ends here.
