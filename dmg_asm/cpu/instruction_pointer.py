"""
A set of helper functions used during processing of instructions.
"""
from singleton_decorator import singleton
from ..core.convert import Convert as EC
from ..core.expression import Expression
from ..core.exception import ExpressionBoundsError, ExpressionSyntaxError

###############################################################################
# Manages the instruction pointer position. Nececesary to compute
# label locations.
#


@singleton
class InstructionPointer:
    """The CPU's IP or Instruction Pointer."""
    _pointer = None
    _section_base = None

    def __init__(self):
        """IP Initializer."""
        self._pointer = 0x0000
        self._section_base = 0x00

    def __repr__(self):
        """Return the string representation of the IP."""
        desc = "No value"
        if self._pointer is not None:
            desc = f"Address: {self._pointer:04x}".upper()
        return desc

    @property
    def pointer(self) -> int:
        """Returns the current location or IP."""
        return self._pointer

    @pointer.setter
    def pointer(self, value):
        """Set the current location or IP."""
        if value in range(0, 65536):
            # print(f"Setting IP to {hex(value)}")
            self._pointer = value

    def move_pointer_relative(self, val) -> bool:
        """Move the IP relative to it's current position.

        This is another name for move_location_relative()."""
        return self.move_location_relative(val)

    @property
    def location(self) -> int:
        """Return the current location or IP."""
        return self._pointer

    @location.setter
    def location(self, value):
        """Set the current location or IP."""
        if value in range(0, 65536):
            # print(f"IP(): Setting IP to {hex(value)}")
            self._pointer = value

    def move_location_relative(self, val) -> bool:
        """Move the IP relative to it's current position.

        Moves the location (pointer) val distance positive or negative
        relative to the current location. If the move can be made within
        the range of 0 to 65535 then the return value will be True,
        otherwise it will be false.  This method differs from then
        move_relative() method in that the direction is not limited to +/-
        127/128.
        """
        newloc = self._pointer + val
        if 65536 > newloc >= 0:
            # print(f"IP(): Moving pointer {hex(val)} bytes. New Address =
            # {hex(newloc)}")
            self._pointer = newloc
            return True
        return False

    @property
    def base_address(self):
        """Return the base address of the IP.

        This is based upon the SECTION in which the IP is in.
        """
        return self._section_base

    @base_address.setter
    def base_address(self, new_value):
        """Set the base address of this instruction pointer.

        This relates to the SECTION value that the IP is in.
        """
        # A value can be an expression such as $FFD2
        address = EC(Expression(new_value)).to_decimal().raw_str
        # address = _conv.decimal_from_expression(new_value)
        # print(f"IP: Setting Address to {hex(address)}")
        if address is None:
            address = 0x0000
        else:
            self._section_base = address
            self._pointer = address

    def offset_from_base(self) -> int:
        """Return the offset value from the original base of the IP."""
        return self.location - self.base_address

    def move_relative(self, relative):
        """Move the IP relative by a single byte's value.

        relative is a single byte. 0 - 127 is positive branch
        128 - 255 is negative branch. The relative value must be
        a positive number from 0 - 255.
        """
        rc = False
        if relative in range(0, 255):
            neg = relative >> 7
            displacement = ((relative ^ 255) + 1) * -1 if neg else relative
            if self._pointer + displacement > 0:
                self._pointer += displacement
                rc = True
        return rc
