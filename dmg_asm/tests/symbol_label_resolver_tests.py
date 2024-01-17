"""DMG Assembler unit tests."""

# import os
import unittest
from icecream import ic

from ..tokens import TokenType, Tokenizer, TokenGroup
from ..core.constants import SYM
from ..core.reader import BufferReader
from ..core.label import Label, Labels
from ..core.expression import Expression
from ..cpu.mnemonic import Mnemonic

ASM_1 = """
USER_IO    EQU $FF00

ld hl, USER_IO
"""


class SymbolAndLabelUnitTests(unittest.TestCase):
    """Token Unit Tests."""

    labels: Labels

    def setUp(self):
        self.labels = Labels()
        self.labels.clear()

    def tearDown(self):
        self.labels.clear()

    def test_tokenize_label(self):
        """Tokenize a line with a label."""
        line = "DEF USER_IO EQU $FF00"
        tokens = Tokenizer().tokenize_string(line)
        # tokens[1] is the Label, tokens[3] is the value
        lab = Label(name=tokens[1].value,
                    value=Expression(tokens[3].value))
        self.assertTrue(lab.name == "USER_IO")
        self.assertTrue(lab.value == Expression("$FF00"))
        self.assertTrue(self.labels.push(lab))

    def test_labels_store_push(self):
        """Test the Labels store with two Label objects."""
        line = "DEF USER_IO EQU $FF00"
        tokens = Tokenizer().tokenize_string(line)
        # tokens[1] is the Label, tokens[3] is the value
        lab = Label(name=tokens[1].value,
                    value=Expression(tokens[3].value))
        self.assertTrue(self.labels.push(lab))

        line2 = "PARALLAX_DELAY EQU $02"
        tokens2 = Tokenizer().tokenize_string(line2)
        # tokens2[0] is the Label, tokens[2] is the value
        lab2 = Label(name=tokens2[0].value,
                     value=Expression(tokens2[2].value))
        self.assertTrue(self.labels.push(lab2))
        self.assertTrue(len(self.labels) == 2)

    def test_labels_store_and_find(self):
        """Test the Labels store with two Label objects."""
        populate_labels()
        labx = Labels().find("USER_IO")
        self.assertTrue(labx is not None,
                        "The stored label was not found.")
        self.assertTrue(labx.name == "USER_IO",
                        "The Label found was not the correct one.")
        self.assertTrue(labx.value == Expression("$FF00"))

    def test_labels_find_and_replace(self):
        """Test the Labels store with two Label objects."""
        populate_labels()
        labx = Labels().find("USER_IO")
        self.assertTrue(labx.value == Expression("$FF00"))
        lab = Label("USER_IO", Expression("$1234"))
        self.assertTrue(Labels().push(lab, replace=True))
        lab2 = Labels().find("USER_IO")
        self.assertTrue(lab2.value == Expression("$1234"))
        print(lab2)

    def test_tokenize_lines(self):
        """Test tokenization of a small set of program lines."""
        _reader = BufferReader(ASM_1)
        _line = ''
        _success = False
        while _reader.is_eof() is False:
            _line = _reader.read_line()
            if _line and len(_line) > 0:
                groups = Tokenizer().tokenize_string(_line)
                if len(groups) == 0:
                    continue
                else:
                    _success = True
        self.assertTrue(_success)

    #  End of unit tests


def print_group(group):
    """Print the token group."""
    ic("--------------------------------------")
    ic("Token Group(s):")
    index = 0
    for token in group.tokens():
        grouping = f"{index:02d}: {str(token)}"
        ic(grouping)
        index += 1
    ic("--------------------------------------")


def print_line(line_str):
    """Print the line to parse."""
    return
    ic("++++++++++++++++++++++++++++++++++++++")
    ic("Code to parse:")
    ic(line_str)
    ic("++++++++++++++++++++++++++++++++++++++")


def populate_labels():
    """Test the Labels store with two Label objects."""
    line = "DEF USER_IO EQU $FF00"
    tokens = Tokenizer().tokenize_string(line)
    # tokens[1] is the Label, tokens[3] is the value
    lab = Label(name=tokens[1].value,
                value=Expression(tokens[3].value))
    Labels().push(lab)
    line2 = "PARALLAX_DELAY EQU $02"
    tokens = Tokenizer().tokenize_string(line2)
    # tokens[0] is the Label, tokens[2] is the value
    lab2 = Label(name=tokens[0].value,
                 value=Expression(tokens[2].value))
    Labels().push(lab2)
