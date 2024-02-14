"""Classes that convert text into Tokens."""

from __future__ import annotations
from .token import Token, TokenType


class TokenGroup:
    """Group a set of tokens related tokens together as a single unit.

    This class is typically returned from the 'Tokenizer' class as a result
    of parsing a line of text. The TokenGroup represents an array of tokens
    that are created by parsing a line of text (see Tokenizer).
    """

    def __init__(self):
        """Initialize the object."""
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

    def __getitem__(self, index):
        """Retrieve an individual token by key."""
        if isinstance(index, slice):
            return self._group_store.__getitem__(index)
        return self.element_at(index)

    def __len__(self):
        """Return the number of keys in the dictionary."""
        return len(self._group_store)

    def __iter__(self):
        return self._group_store.__iter__()

    def __reversed__(self):
        return self._group_store.__reversed__()

    @classmethod
    def from_token_list(cls, tokens: list) -> TokenGroup | None:
        """Return a new TokenGroup from a list of TokenFactory elements."""
        if tokens is None or len(tokens) == 0:
            return None
        new_grp = TokenGroup()
        for element in tokens:
            new_grp.add(element)
        return new_grp

    def index_of(self, token: Token) -> int | None:
        """Return the index in the group of the specified token.

        Token equality is defined as an equal token value and token type."""
        for index, item in enumerate(self._group_store):
            if item == token:
                return index
        return None

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

    def find_first_type(self, token_type: TokenType) -> int | None:
        """Return the index in the group that matches the passed type.

        If the type appears more than once in the group, only the first one
        found is returned.
        """
        for index, item in enumerate(self._group_store):
            if item.type == token_type:
                return index
        return None

    def add(self, token: Token):
        """Add an aditional token to the end of tokens group."""
        if token is None:
            raise ValueError("Passed token must have a value.")
        self._group_store.append(token)

    def remove(self, index: int) -> Token | None:
        """Remove the Token in the group at the specified index."""
        if index not in range(0, len(self._group_store)):
            raise IndexError("Index out of bounds.")
        return self._group_store.pop(index)

    def tokens(self) -> list:
        """Return a list of Tokens in the group."""
        return self._group_store

    def element_at(self, index: int) -> Token:
        """Return the Token at the 0-based index provided."""
        if 0 <= index < len(self._group_store):
            return self._group_store[index]
        raise IndexError
        # raise IndexError("Index out of range")
