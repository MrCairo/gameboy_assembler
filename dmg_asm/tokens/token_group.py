"""Classes that convert text into Tokens."""

# from __future__ import annotations
from collections import OrderedDict
from icecream import ic
from typing import Optional
from .token import Token


class TokenGroup:
    """Group a set of tokens related tokens together as a single unit."""

    def __init__(self):
        """Initialize the object."""
        # if primary_token is None:
        #     raise ValueError("The primary_token must have a value.")
        self._group_store = []

    def __repr__(self):
        """Represent this object as a printable string."""
        tokens = self.tokens()
        desc = ""
        for tok in tokens:
            desc += tok.__repr__() + "\n"
        return desc

    def __str__(self):
        """Format object definition as a printable string."""
        desc = ""
        for idx, tok in enumerate(self.tokens()):
            desc += f"\n{idx:02d}. {tok.__str__()}"
        return desc

    def __getitem__(self, index: int):
        """Retrieve an individual token by key."""
        return self.element_at(index)

    def __len__(self):
        """Return the number of keys in the dictionary."""
        return len(self._group_store)

    def find_first_value(self, value) -> int | None:
        """Return the index in the group that matches the passed value.

        If the value element appears more than once in the group, only the
        first one found is returned.
        """
        up = value.upper()
        for index, item in enumerate(self._group_store):
            if item.value.upper() == up:
                return index
        return None

    def add(self, token: Token):
        """Add an aditional token to the end of tokens group."""
        if token is None:
            raise ValueError("Passed token must have a value.")
        self._group_store.append(token)

    def tokens(self) -> list:
        """Return a list of Tokens in the group."""
        return self._group_store

    def element_at(self, index: int) -> Token:
        """Return the Token at the 0-based index provided."""
        if 0 <= index < len(self._group_store):
            return self._group_store[index]
        raise IndexError
        # raise IndexError("Index out of range")
