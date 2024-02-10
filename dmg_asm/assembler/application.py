"""The application store that is used to write the application binary."""

from __future__ import annotations
from dataclasses import dataclass

from ..core.expression import Expression
from ..core.exception import ExpressionException


@dataclass
class _Entry:

    address: str
    code: bytearray

    def __init__(self, address: str, code: bytes):
        self.address = address
        self.code = code


class Application:
    """Store sequence of data that builds an application."""

    _app_data = []
    _address: int

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Application, cls).__new__(cls)
            cls.instance._address = "$0000"
            cls._app_data = []
        return cls.instance

    def establish_code_at_address(self, code: bytes,
                                  address: Expression) -> bool:
        """Create a new entry into the app_data with code + address.

        The address stored is the provided address. The internal address is
        set to the new address and then incremented the length of the included
        bytes.

        Return True if the address and code were created and added."""
        if code is None or not isinstance(code, bytes):
            return False
        if address.integer_value < 0:
            return False
        self._app_data.append(_Entry(f"${address.integer_value:04X}", code))
        self._address = address.integer_value + len(code)
        return True

    def append_code(self, code: bytes) -> bool:
        """Append code to the end of the current entry."""
        if len(self._app_data) == 0:
            return False
        entry: _Entry = self._app_data[-1]
        entry.code.append(code)
        self._address += len(code)
        return True

    @property
    def current_address(self) -> int:
        """Return the current address as an integer."""
        return self._address

    @current_address.setter
    def current_address(self, new_value: int) -> None:
        """Set the current address value."""
        if new_value is None or not isinstance(new_value, int):
            raise ValueError("Attempt to set address to an invalid value.")
        if not 0 < new_value < 65536:
            raise ValueError("Attempt to set address to an invalid value.")
        try:
            _ = Expression(f"${new_value:04X}")
        except ExpressionException as err:
            raise err
        self._address = new_value

    @property
    def current_address_as_expression(self) -> Expression:
        """Return the current address as an Expression."""
        return Expression(f"${self._address:04X}")

    def reset(self):
        """Reset Application to an empty state."""
        self._address = 0
        self._app_data = []
