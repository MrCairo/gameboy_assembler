"""
A set of helper functions used during processing of instructions.
"""
from ..core.convert import Convert
from ..core.expression import Expression
from ..core.descriptor import BaseDescriptor
from ..core.exception import ExpressionException

###############################################################################
#
# Manages the instruction pointer position. Nececesary to compute
# label locations.
#


class InstructionPointer:
    """The CPU's IP or Instruction Pointer."""
    _pointer: Expression
    _section_base: Expression

    def __new__(cls):
        """IP Initializer and singleton."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(InstructionPointer, cls).__new__(cls)
            cls.instance._pointer = Expression("0x0000")
            cls.instance._section_base = Expression("0x00")
        return cls.instance

    def __repr__(self) -> str:
        return "InstructionPointer()"

    def __str__(self) -> str:
        """Return the string representation of the IP."""
        desc = "No value"
        if self._pointer is not None:
            desc = f"Address: {self._pointer:04x}".upper()
        return desc

    @property
    def pointer(self) -> Expression:
        """Returns the current location or IP."""
        return self._pointer

    @pointer.setter
    def pointer(self, value: Expression) -> None:
        """Set the current location or IP as a 16-bit value."

        A ValueError will be raised in an 8-bit or base-0 expression
        is passed."""
        if value.descriptor.limits.max != 65536:
            msg = "The IP pointer value must be set to a 16-bit value."
            raise ValueError(msg)
        self._pointer = Expression(f"0{value.integer_value:04d}")

    def move_pointer_relative(self, val: int) -> bool:
        """Move the IP relative to it's current position.

        Moves the location (pointer) val distance positive or negative relative
        to the current location. The resulting value must not move the IP to
        less than 0 or greater than 65535 otherwise a ValueError exception will
        be raised. This method differs from then move_relative() method in that
        the direction is not limited to +/- 127/128."""
        if not isinstance(val, int):
            raise TypeError("The passed in value must be an integer.")
        curr: int = Convert(self._pointer).to_decimal_int()
        curr += val
        if 65536 > curr >= 0:
            self._pointer = Expression(f"0{curr:04d}")
            return True
        msg = "The resulting pointer would not be in the 0-65535 range."
        raise ValueError(msg)

    @property
    def base_address(self) -> Expression:
        """Return the base address of the IP.

        This is based upon the SECTION in which the IP is in.
        """
        return self._section_base

    @base_address.setter
    def base_address(self, new_value: Expression) -> None:
        """Set the base address of this instruction pointer.

        This relates to the SECTION value that the IP is in.
        """
        if not isinstance(new_value, Expression):
            raise TypeError("base_address() must be passed an Expression.")
        if new_value.descriptor.limits.max < 65535:
            raise ValueError("The new base_address must be a 16-bit value.")
        #
        # Convert the current value so that we create two new Expression
        # objects.
        new_base = Convert(Expression(new_value)).to_hex16()
        new_ip = Convert(Expression(new_value)).to_hex16()
        # address = _conv.decimal_from_expression(new_value)
        # print(f"IP: Setting Address to {hex(address)}")
        self._section_base = new_base
        self._pointer = new_ip

    def offset_from_base(self) -> int:
        """Return the offset value from the original base of the IP."""
        curr = Convert(self.pointer).to_decimal_int()
        base = Convert(self._section_base).to_decimal_int()
        return curr - base

    def move_relative(self, relative: Expression) -> bool:
        """Move the IP relative by a single byte's value.

        relative is a single byte. 0 - 127 is positive branch
        128 - 255 is negative branch. The relative value must be
        a positive number from 0 - 255."""
        if isinstance(relative, Expression):
            raise TypeError("base_address() must be passed an Expression.")
        if relative.descriptor.limits.max > 256:
            raise ValueError("The new base_address must be an 8-bit value.")
        rel = Convert(relative).to_decimal_int()
        neg = rel >> 7
        displacement = ((rel ^ 255) + 1) * -1 if neg else rel
        try:
            self.move_pointer_relative(displacement)
        except (TypeError, ValueError, ExpressionException):
            return False
        return True
