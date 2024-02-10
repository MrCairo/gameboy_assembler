import unittest

from ..assembler.application import Application
# from ..core import Expression
from ..directives.mnemonic import Mnemonic
# from ..directives.storage import Storage
from ..tokens.tokenizer import TokenGroup, Tokenizer


class ApplicationUnitTests(unittest.TestCase):
    """Test the application classes."""

    def setUp(self):
        Application().address = 0

    def test_application_address(self):
        """Basic test of the Application class."""
        group: TokenGroup = Tokenizer().tokenize_string("LD BC, $FFD2")
        self.assertIsNotNone(group)
        inst = Mnemonic(group)
        self.assertIsNotNone(inst)
        print("******************")
        hex_str = bytes_to_string(inst.instruction_detail.code)
        print(hex_str)


def bytes_to_string(code: bytes) -> str:
    """Convert code in bytes to a string of hex values."""
    hexi = code.hex()
    out_str = ""

    for i in range(0, len(hexi), 2):
        out_str += f"{hexi[i:i+2]} "
    return out_str
