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

    def __getitem__(self, index: int):
        """Retrieve an individual token by key."""
        return self.element_at(index)

    def __len__(self):
        """Return the number of keys in the dictionary."""
        return len(self._group_store)

    def __iter__(self):
        return self._group_store.__iter__()

    def __reversed__(self):
        return self._group_store.__reversed__()

    @classmethod
    def group_from_token_chain(cls, start_token: Token):
        """Create a new TokenGroup with existing Tokens from another group."""
        new_group = TokenGroup()
        if start_token is not None and isinstance(start_token, Token):
            new_group.add(start_token.shallow_copy())
            _next_tok = start_token.next
            while _next_tok is not None:
                new_group.add(_next_tok.shallow_copy())
                _next_tok = _next_tok.next
        return new_group

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
