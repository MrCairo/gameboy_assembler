"""DMG Assembler unit tests."""

# import os
import unittest

# pylint: disable=relative-beyond-top-level
from ..cpu import InstructionPointer
from ..core import Expression
from ..core.exception import ExpressionException


class IPUnitTests(unittest.TestCase):
    """Directive Unit Tests."""

    def setUp(self) -> None:
        InstructionPointer().pointer = Expression("0x0000")

    def test_can_set_ip(self):
        """Test if the Instruction Pointer can be set."""
        self.assertIsNotNone(InstructionPointer().pointer)
        start: int = InstructionPointer().pointer.integer_value
        self.assertTrue(start == 0)
        dest = "0x100"
        try:
            InstructionPointer().pointer = Expression(dest)
        except ValueError:
            self.fail(f"Cannot set InstructionPointer to {dest}")
        self.assertTrue(InstructionPointer().pointer.integer_value == 256)

    def test_can_move_ip_negative(self):
        """Test if the Instruction Pointer can be set."""
        self.assertIsNotNone(InstructionPointer().pointer)
        start: int = InstructionPointer().pointer.integer_value
        self.assertTrue(start == 0)
        dest = Expression("0x1100")
        try:
            InstructionPointer().move_pointer_relative(dest.integer_value)
        except (ValueError, TypeError, ExpressionException):
            self.fail(f"Cannot move InstructionPointer {dest} bytes")
        self.assertTrue(InstructionPointer().pointer.integer_value == 4352)
        start = InstructionPointer().pointer.integer_value
        dest: int = -495
        try:
            InstructionPointer().move_pointer_relative(dest)
        except ValueError:
            self.fail(f"Cannot move InstructionPointer relative {dest} bytes.")
        # 4352 - 495 == 3857
        self.assertTrue(InstructionPointer().pointer.integer_value == 3857)

    def test_can_move_ip_positive(self):
        """Test if the Instruction Pointer can be set."""
        self.assertIsNotNone(InstructionPointer().pointer)
        base: int = InstructionPointer().pointer.integer_value
        self.assertTrue(base == 0)
        starting = Expression("0x1234")  # 4660
        try:
            InstructionPointer().pointer = starting
        except (ValueError, TypeError, ExpressionException):
            self.fail(f"Cannot move InstructionPointer {starting} bytes")
        self.assertTrue(InstructionPointer().pointer.integer_value == 4660)
        base = InstructionPointer().pointer.integer_value
        rel: int = 1000
        try:
            InstructionPointer().move_pointer_relative(rel)
        except ValueError:
            self.fail(f"Cannot move InstructionPointer relative {rel} bytes.")
        # 4660 + 1000 = 5660
        final = base + rel
        self.assertTrue(InstructionPointer().pointer.integer_value == final)

    def test_can_move_ip_8bit_relative(self):
        """Test if the Instruction Pointer can be set."""
        self.assertIsNotNone(InstructionPointer().pointer)
        start: int = InstructionPointer().pointer.integer_value
        self.assertTrue(start == 0)
        dest = Expression("0xFFD2")
        try:
            InstructionPointer().pointer = dest
        except (ValueError, TypeError, ExpressionException):
            msg = f"Cannot move InstructionPointer {dest.integer_value} bytes"
            self.fail(msg)
        start = InstructionPointer().pointer.integer_value
        self.assertTrue(start == 65490)
        rel = Expression("0xFB")  # Move back 5 bytes (5 with 2's compliment)
        try:
            InstructionPointer().move_relative(rel)
        except ValueError:
            self.fail("Cannot move InstructionPointer -5 relative bytes.")
        result = InstructionPointer().pointer.integer_value
        self.assertTrue(result == start - 5)


#  End of unit tests
