"""The application store that is used to write the application binary."""

from __future__ import annotations
from dataclasses import dataclass

from ..core.expression import Expression
from ..core.constants import NUMERIC_BASES


@dataclass
class _Entry:

    address: str
    code: bytearray


class Application:
    """Store sequence of data that builds an application."""

    _app_data = []
    _address: int
    _to_resolve = []

    def __new__(cls):
        """Implement a singleton by returning the existing or new instance."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Application, cls).__new__(cls)
            cls.instance._address = "$0000"
            cls._app_data = []
        return cls.instance

    def create_new_address_entry(self, address: Expression) -> bool:
        """Create a new entry into the app_data with code + address.

        The address stored is the provided address. The internal address is
        set to the new address and then incremented the length of the included
        bytes.

        Return True if the address and code were created and added.
        """
        if not isinstance(address, Expression):
            raise ValueError("address was not a valid Expression object.")
        if address.base not in NUMERIC_BASES:
            return False
        self._app_data.append(_Entry(f"${address.integer_value:04X}",
                                     bytearray()))
        self._address = address.integer_value
        return True

    def append_code(self, code: bytes) -> bool:
        """Append code to the end of the current entry."""
        if len(self._app_data) == 0:
            addr_str = f"0{self.current_address}"
            self._app_data.append(_Entry(addr_str, bytearray(code)))
        else:
            entry: _Entry = self._app_data[-1]
            entry.code.extend(code)
        self._address += len(code)
        return True

    @property
    def current_address(self) -> int:
        """Return the current address as an integer."""
        return self._address

    @property
    def current_address_as_expression(self) -> Expression:
        """Return the current address as an Expression."""
        return Expression(f"${self._address:04X}")

    def reset(self):
        """Reset Application to an empty state."""
        self._address = 0
        self._app_data = []
