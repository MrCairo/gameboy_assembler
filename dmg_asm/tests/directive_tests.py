"""DMG Assembler unit tests."""

# import os
import unittest

# pylint: disable=relative-beyond-top-level
from ..core import Convert
from ..core.expression import Expression
from ..directives import Equate, Define
from ..directives.section import Section
from ..directives.sections import Sections
from ..directives.storage import Storage
from ..tokens import TokenGroup, Tokenizer


class DirectiveUnitTests(unittest.TestCase):
    """Directive Unit Tests."""

    @classmethod
    def setUpClass(cls):
        Sections()

    def setUp(self):
        Sections().clear()

    # ===== Equate Tests ===================================
    def test_equate_from_string(self):
        """Test Equate class."""
        equ = Equate.from_string("VAR_NAME EQU $0100")
        self.assertTrue(equ is not None)
        self.assertTrue(equ.label == "VAR_NAME")
        self.assertEqual(Convert(equ.expression).to_decimal_int(),
                         256, "Expression not euqal to 256.")

    # ===== Define Tests ===================================
    def test_define_from_string(self):
        """Test Define class."""
        equ = Define.from_string("DEF my_var EQU $1000")
        self.assertTrue(equ is not None)
        self.assertTrue(equ.name.upper() == "MY_VAR")
        self.assertEqual(Convert(equ.value).to_decimal_int(),
                         4096, "Expression not euqal to 4096.")

    # ===== Storage Tests ==================================
    def test_storage_ds_single_fill(self):
        """Test the DS Directive supplied as a string."""
        source = 'DS $10'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        data = stor.bytes()
        self.assertIsNotNone(data)

    def test_only_ds_storage(self):
        """Test the DS Directive supplied as a string."""
        source = 'DS'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        data = stor.bytes()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 1)

    def test_storage_multi_fill_ds_repeat(self):
        """Test the DS Directive supplied as a string."""
        source = 'DS $10 $01, $02, $03'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        data = stor.bytes()
        self.assertIsNotNone(data)

    def test_storage_multi_fill_ds_exceeds(self):
        """Test the DS Directive supplied as a string."""
        source = 'DS $05 $01, $02, $03, $04, $05, $06, $07'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        data = stor.bytes()
        self.assertIsNotNone(data)

    def test_storage_db_single(self):
        """Test the DB storage directive with just a single byte."""
        source = 'DB $FF'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        self.assertIsNotNone(stor)
        data = stor.bytes()
        self.assertIsNotNone(data)

    def test_storage_db_multi(self):
        """Test the DB storage directive with just a single byte."""
        source = 'DB $FF $10, $D2, $1234'  # $1234 should truncate to $34
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        self.assertIsNotNone(stor)
        data = stor.bytes()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 4)

    def test_storage_db_multi_string(self):
        """Test the DB storage directive with just a single byte."""
        source = 'DB $FF "Hello"'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        self.assertIsNotNone(stor)
        data = stor.bytes()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 6)

    def test_storage_dw_single(self):
        """Test the DB storage directive with just a single byte."""
        source = 'DW $FFD2'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        self.assertIsNotNone(stor)
        data = stor.bytes()
        self.assertIsNotNone(data)

    def test_storage_dw_multiple(self):
        """Test the DB storage directive with just a single byte."""
        source = 'DW $FFD2 $1234 $42'
        group = Tokenizer().tokenize_string(source)
        self.assertTrue(len(group) > 0)
        stor = Storage(group)
        self.assertIsNotNone(stor)
        data = stor.bytes()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) == 6)

    # ===== Section and Sections Tests =====================

    def test_tokenize_section_from_string(self):
        """Test the SECTION Directive supplied as a string."""
        section = 'SECTION "CoolStuff", WRAM0, BANK[2]'
        group = Tokenizer().tokenize_string(section)
        self.assertTrue(len(group) > 0)

    def test_section_can_get_label_and_mem_block(self):
        """Find first label and enclosing delmiters."""
        code = 'SECTION "coolstuff", WRAM0[$4567]'
        group: TokenGroup = Tokenizer().tokenize_string(code)
        self.assertTrue(group is not None)
        sec: Section = Section(group)
        self.assertIsNotNone(sec.label)
        self.assertTrue(sec.label.lower() == "coolstuff")
        self.assertIsNotNone(sec.memory_block)
        self.assertTrue(sec.memory_block.name == "WRAM0")
        self.assertIsNotNone(sec.memory_block_offset)
        test_expr = Expression("$4567")
        self.assertTrue(sec.memory_block_offset == test_expr)

    def test_sections_store_items(self):
        """Test the Sections store/catalog."""
        code = 'SECTION "coolstuff", WRAM0[$4567]'
        group: TokenGroup = Tokenizer().tokenize_string(code)
        sec1: Section = Section(group)
        self.assertIsNotNone(sec1)
        self.assertTrue(Sections().push(sec1))
        code = 'SECTION "MAIN_ENTRY", ROMX, BANK[2]'
        sec2: Section = Section(Tokenizer().tokenize_string(code))
        self.assertIsNotNone(sec2)
        self.assertTrue(Sections().push(sec2))
        self.assertTrue(len(Sections()) == 2)

    def test_sections_find_items(self):
        """Test if the Sections catalog will find the correct items."""
        self._setup_sections()
        found1: int = Sections().find_first_index("CoolStuff")
        self.assertIsNotNone(found1)
        sec1: Section = Sections()[found1]
        self.assertIsNotNone(sec1)
        self.assertTrue(sec1.label.upper() == "COOLSTUFF")
        found2: int = Sections().find_first_index("main_entry")
        self.assertIsNotNone(found2)
        sec2: Section = Sections()[found2]
        self.assertIsNotNone(sec2)
        self.assertTrue(sec2.label.upper() == "MAIN_ENTRY")

    def test_sections_remove_and_find_item(self):
        """Test if the Sections catalog will find the correct items."""
        self._setup_sections()
        found1: int = Sections().find_first_index("CoolStuff")
        self.assertIsNotNone(found1)
        sec1: Section = Sections()[found1]
        self.assertIsNotNone(sec1)
        self.assertTrue(sec1.label.upper() == "COOLSTUFF")
        found2: int = Sections().find_first_index("main_entry")
        self.assertIsNotNone(found2)
        sec2: Section = Sections()[found2]
        self.assertIsNotNone(sec2)
        self.assertTrue(sec2.label.upper() == "MAIN_ENTRY")
        try:
            Sections().pop("CoolStuff")
        except (TypeError, ValueError):
            self.fail("Unable to remove existing Section.")
        found3: int = Sections().find_first_index("main_entry")
        self.assertIsNotNone(found3)
        self.assertTrue(found3 == 0)
        sec3 = Sections()[found3]
        self.assertIsNotNone(sec3)
        self.assertTrue(sec3.label.upper() == "MAIN_ENTRY")
        self.assertTrue(len(Sections()) == 1)

    def test_sections_can_replace_item(self):
        """Test if the Sections catalog will find the correct items."""
        self._setup_sections()
        found1: int = Sections().find_first_index("CoolStuff")
        self.assertIsNotNone(found1)
        sec1: Section = Sections()[found1]
        self.assertIsNotNone(sec1)
        self.assertTrue(sec1.label.upper() == "COOLSTUFF")
        code = 'SECTION "coolstuff", ROM0, ALIGN[8]'
        sec2: Section = Section(Tokenizer().tokenize_string(code))
        self.assertTrue(Sections().replace(sec2))
        found2: int = Sections().find_first_index("coolstuff")
        self.assertIsNotNone(found2)
        sec3: Section = Sections()[found2]
        self.assertIsNotNone(sec3)
        self.assertTrue(sec3.alignment == 8)
        self.assertTrue(sec3.memory_block.name == "ROM0")

    # ===== Helper functions ===============================

    def _setup_sections(self):
        """Add some initial sections to the Sections() catalog."""
        code = 'SECTION "coolstuff", WRAM0[$4567]'
        sec1: Section = Section(Tokenizer().tokenize_string(code))
        Sections().push(sec1)
        code = 'SECTION "MAIN_ENTRY", ROMX, BANK[2]'
        sec2: Section = Section(Tokenizer().tokenize_string(code))
        Sections().push(sec2)


#  End of unit tests
